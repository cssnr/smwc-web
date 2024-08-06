import datetime
import ftplib
import logging
import os
import re
import requests
import statsd
import tarfile
import tempfile
import urllib3
from urllib import parse
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.text import slugify
from bs4 import BeautifulSoup
from celery import shared_task
from home.models import Hacks, Webhooks

logger = logging.getLogger('celery')
c = statsd.StatsClient(settings.STATSD_HOST, settings.STATSD_PORT, settings.STATSD_PREFIX)
urllib3.disable_warnings()


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 1, 'countdown': 240})
def process_hacks():
    logger.debug('process_hacks: executed')
    waiting, r = SmwCentral.get_waiting()
    if not waiting:
        logger.debug('No waiting hacks.')
        return 'No waiting hacks.'

    logger.debug('Total Waiting Hacks: %s\n%s', len(waiting), waiting)
    errors = 0
    for i, h in enumerate(waiting):
        logger.debug('Processing hack %s/%s.', i, len(waiting))
        try:
            href = h['href']
            logger.debug('href: %s', href)
            logger.debug('text: %s', h.text)
            hack_url = href if href.startswith('http') else settings.APP_SMWC_URL + href
            logger.debug('hack_url: %s', hack_url)
            query = parse.parse_qs(parse.urlparse(hack_url).query)
            smwc_id = SmwCentral.verify_hack(h, query['id'][0].strip())
            if not smwc_id:
                logger.debug('Unable to verify hack: %s', h.text)
                continue

            logger.debug('smwc_id: %s', smwc_id)
            hack, created = Hacks.objects.get_or_create(smwc_id=smwc_id)
            logger.debug('created: %s', created)
            if not created:
                logger.debug('not created smwc_id: %s', smwc_id)
                continue

            logger.debug('tasks.process_hacks.created')
            c.incr('tasks.process_hacks.created')
            hack.name = h.text
            hack.smwc_href = href
            SmwCentral.update_hack_info(hack)
            SmwCentral.download_rom(hack)
            hack.save()
            process_alert.delay(hack.pk)
            logger.debug('deleting cache key for template fragment: roms_body')
            key = make_template_fragment_key('roms_body')
            cache.delete(key)
            logger.info('New Hack: %s | %s | %s', hack.smwc_id, hack.name, hack.get_hack_url())

        except Exception as error:
            c.incr('tasks.process_hacks.errors')
            errors += 1
            logger.exception(error)
            continue

    return 'Processed {} hacks with {} errors.'.format(len(waiting), errors)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60}, rate_limit='10/m')
def process_alert(hack_pk):
    hack = Hacks.objects.get(pk=hack_pk)
    message = gen_discord_message(hack)
    logger.debug(message)
    hooks = Webhooks.objects.all()
    if not hooks:
        logger.debug('No hooks found, nothing to do.')
        return

    for hook in hooks:
        if not hook.active:
            continue
        logger.debug('Sending alert to: %s', hook.owner_username)
        send_alert.delay(hook.id, message)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def send_alert(hook_pk, message):
    try:
        hook = Webhooks.objects.get(pk=hook_pk)
        body = {'content': message}
        r = requests.post(hook.webhook_url, json=body, timeout=30)
        c.incr('tasks.send_alert.status_codes.{}'.format(r.status_code))
        if r.status_code == 404:
            logger.warning('Hook %s removed by owner %s - %s',
                           hook.hook_id, hook.owner_username, hook.webhook_url)
            hook.delete()
            c.incr('tasks.send_alert.hook_delete')
            return '404: Hook removed by owner and deleted from database.'

        if not r.ok:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()

        return '{}: {}'.format(r.status_code, r.content.decode(r.encoding))

    except Exception as error:
        c.incr('tasks.send_alert.errors')
        logger.exception(error)
        raise


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60})
def send_discord_message(url, message):
    try:
        body = {'content': message}
        r = requests.post(url, json=body, timeout=30)
        c.incr('tasks.send_discord_message.status_codes.{}'.format(r.status_code))
        if not r.ok:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()
        return '{}: {}'.format(r.status_code, r.content.decode(r.encoding))

    except Exception as error:
        c.incr('tasks.send_discord_message.errors.')
        logger.exception(error)
        raise


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 3600})
def backup_hacks():
    logger.debug('backup_hacks: executed')
    tf = tempfile.NamedTemporaryFile(dir='/tmp')
    df = tempfile.NamedTemporaryFile(dir='/tmp')
    logger.debug('tf.name: %s', tf.name)
    try:
        ts = int(datetime.datetime.now().timestamp())
        logger.debug('ts: %s', ts)
        mysql_dump(df.name)
        tar = tarfile.open(tf.name, 'w:gz')
        tar.add(settings.APP_ROMS_DIR, arcname=f'roms-{ts}')
        tar.add(df.name, arcname=f"{settings.DATABASES['default']['NAME']}-{ts}.sql")
        tar.close()
        ftp_upload_file(tf.name, settings.FTP_DIR, f'roms-{ts}.tar.gz')
        ftp_cleanup.delay()
    finally:
        logger.debug('backup_hacks: finally')
        tf.close()
        df.close()


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 3600})
def ftp_cleanup(directory=None, keep_files=10, ls_pattern=None):
    logger.debug('ftp_cleanup: executed')

    directory = settings.FTP_DIR
    keep_files = settings.FTP_KEEP_FILES
    ls_pattern = 'roms-*.tar.gz'

    logger.debug('directory: %s', directory)
    logger.debug('keep_files: %s', keep_files)
    logger.debug('ls_pattern: %s', ls_pattern)

    ftp = ftplib.FTP(host=settings.FTP_HOST, user=settings.FTP_USER, passwd=settings.FTP_PASS)
    try:
        rdir = directory.rstrip('/') + '/' + ls_pattern.lstrip('/') if ls_pattern else directory
        logger.debug('rdir: %s', rdir)
        dl = ftp.nlst(rdir)
        logger.debug('dl: %s', dl)
        dl.sort(reverse=True)
        keeping = []
        if len(dl) <= int(keep_files):
            logger.debug('Found %s files but keeping %s.', len(dl), keep_files)
            return

        for _ in range(int(keep_files)):
            keeping.append(dl.pop(0))
        for file in dl:
            logger.debug('Deleting file: %s', file)
            ftp.delete(file)
        logger.debug('keeping: %s', keeping)
    finally:
        logger.debug('ftp_cleanup: finally')
        ftp.quit()


def mysql_dump(output_file_path):
    import subprocess
    command = 'mysqldump -h {} -u {} -p"{}" {} > {}'.format(
        settings.DATABASES['default']['HOST'],
        settings.DATABASES['default']['USER'],
        settings.DATABASES['default']['PASSWORD'],
        settings.DATABASES['default']['NAME'],
        output_file_path,
    )
    result = subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    logger.debug(result)
    if result != 0:
        logger.error(result)
        raise Exception('mysqldump error')
    return result


def ftp_upload_file(filepath, directory, remote_filename=None):
    r_file = os.path.join(directory, remote_filename or os.path.basename(filepath))
    ftp = ftplib.FTP(host=settings.FTP_HOST, user=settings.FTP_USER, passwd=settings.FTP_PASS)
    try:
        dl = ftp.nlst(directory)
        if (remote_filename or os.path.basename(filepath)) in dl:
            raise Exception(f'Remote file already exists: {r_file}')
        with open(filepath, 'rb') as file:
            ftp.storbinary(f'STOR {r_file}', file)
    finally:
        ftp.quit()


def get_short_url(long_url, title=None, tags=None, domain=None):
    url = 'https://api-ssl.bitly.com/v4/bitlinks'
    headers = {
        'Authorization': 'Bearer {}'.format(settings.BITLY_ACCESS_TOKEN),
        'Content-Type': 'application/json',
    }
    data = {'long_url': long_url}
    if title:
        data['title'] = title
    if title:
        data['tags'] = tags
    if title:
        data['domain'] = domain
    r = requests.post(url, json=data, headers=headers, timeout=15)
    if not r.ok:
        return None
    return r.json()['link']


def gen_discord_message(hack):
    message = 'New Hack: **{}**\nSMWC URL: {}'.format(hack.name, hack.get_hack_url())
    if hack.get_archive_url():
        message += '\nArchive URL: {}'.format(hack.get_archive_url())
    if hack.get_patcher_url():
        short_url = get_short_url(hack.get_patcher_url())
        if short_url:
            logger.debug('short_url: %s', short_url)
            message += '\nPatcher URL: <{}>'.format(short_url)
    if hack.difficulty:
        message += '\nDifficulty: **{}**'.format(hack.difficulty)
    if hack.length:
        message += '\nLength: **{}**'.format(hack.length)
    if hack.authors:
        message += '\nAuthors: **{}**'.format(hack.authors)
    if hack.demo:
        message += '\n**This hack is a DEMO**'
    if hack.featured:
        message += '\n**This hack is a FEATURED**'
    if hack.description:
        max_desc = 1800 - len(message)
        message += '\n```\n{}\n```'.format(hack.description[:max_desc])
    return message


class SmwCentral(object):
    @staticmethod
    def get_waiting():
        # new_hacks = 'https://www.smwcentral.net/?p=section&s=smwhacks&u=1'  # old code
        new_hacks = 'https://www.smwcentral.net/?p=section&s=smwhacks&u=1&locale=en-US'
        r = requests.get(new_hacks, timeout=30)
        c.incr('tasks.get_waiting.status_codes.{}'.format(r.status_code))
        soup = BeautifulSoup(r.content.decode(r.encoding), 'html.parser')
        search_string = '/\?p=section&a=details&id='
        # search_string = r'^/\?p=section&a=details&id=\d+$'  # new code not used
        s = soup.findAll('a', attrs={'href': re.compile(search_string)})
        # s = soup.find_all('a', href=re.compile(r'^/\?p=section&a=details&id=\d+$'))  # new code not used
        return s, r

    @staticmethod
    def verify_hack(h, smwc_id):
        if not smwc_id.isdigit():
            logger.debug('New hack has non-numeric ID: %s', smwc_id)
            return False
        smwc_id = int(smwc_id)
        if smwc_id < settings.APP_MIN_HACK_ID:
            logger.debug('New hack below min ID: %s', smwc_id)
            return False
        try:
            if h.parent.has_attr('class'):
                if h.parent.attrs['class'][0] == 'rope':
                    logger.debug('New hack parent has class rope: %s', smwc_id)
                    return False
            if h.previous_sibling.startswith('Tip') or h.text == 'Floating IPS':
                logger.debug('New hack detected in as tip: %s', smwc_id)
                return False
            return smwc_id

        except Exception as error:
            logger.debug(error)
            return False

    @staticmethod
    def update_hack_info(hack):
        try:
            logger.debug('rom_url: %s', hack.get_hack_url())
            r = requests.get(hack.get_hack_url(), verify=False, timeout=30)
            c.incr('tasks.update_hack_info.status_codes.{}'.format(r.status_code))
            if not r.ok:
                logger.error('Error retrieving smwc webpage: %s', r.status_code)
                r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            details_table = soup.find('table', class_='list')
            details_rows = details_table.find_all('tr')
            data = {}
            for row in details_rows:
                field = row.find('td', class_='field')
                value = row.find('td', class_='name') or row.find('td', class_=None)
                if field and value:
                    data[field.text.strip(':')] = value.text.strip()
            req = ['Name', 'Author', 'Submitted', 'Demo', 'Featured', 'Length',
                   'Type', 'Description', 'Tags', 'Comments', 'Rating']
            for x in req:
                if x not in data:
                    data[x] = None
            download_section = soup.find('div', class_='download-section')
            # hack.download_url = 'https:' + download_section.find('a', class_='button action')['href']  # old code
            hack.download_url = download_section.find('a', class_='button action')['href']
            hack.difficulty = data.get('Type', 'Unknown')
            hack.authors = data.get('Author', 'Unknown')
            hack.length = data.get('Length', 'Unknown')
            hack.description = data.get('Description', 'Unknown')
            hack.demo = True if data.get('Demo') == 'Yes' else False
            hack.featured = True if data.get('Featured') == 'Yes' else False
        except Exception as error:
            logger.exception(error)

    @staticmethod
    def download_rom(hack):
        if not hack.download_url:
            logger.error('Hack PK %s has no download_url', hack.pk)
            return

        logger.info('Download URL: %s', hack.download_url)
        r = requests.get(hack.download_url, verify=False, timeout=30)
        c.incr('tasks.download_rom.status_codes.{}'.format(r.status_code))
        if not r.ok:
            logger.error('Error retrieving rom download archive: %s', r.status_code)
            logger.error(r.content)
            r.raise_for_status()

        parsed = parse.unquote(os.path.basename(parse.urlparse(hack.download_url).path))
        logger.debug('parsed: %s', parsed)
        name, extension = os.path.splitext(parsed)
        logger.debug('name: %s', name)
        logger.debug('extension: %s', extension)
        slug = slugify(hack.name) if hack.name else slugify(name)
        file_name = '{}-{}{}'.format(slug, hack.smwc_id, extension)
        logger.debug('file_name: %s', file_name)
        year_month = datetime.datetime.now().strftime('%Y/%B')
        file_dir = os.path.join(settings.APP_ROMS_DIR, year_month)
        logger.debug('file_dir: %s', file_dir)
        file_uri = os.path.join(year_month, file_name)
        logger.debug('file_uri: %s', file_uri)
        hack.file_uri = file_uri
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_path = os.path.join(file_dir, file_name)
        logger.debug('file_path: %s', file_path)
        with open(file_path, 'wb') as f:
            f.write(r.content)
            f.close()
