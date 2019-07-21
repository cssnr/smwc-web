from __future__ import absolute_import, unicode_literals
import datetime
import logging
import os
import re
import requests
import urllib3
from urllib import parse
from django_statsd.clients import statsd
from django.conf import settings
from django.utils.text import slugify
from bs4 import BeautifulSoup
from celery import task
from home.functions import get_short_url
from home.models import Hacks, Webhooks

logger = logging.getLogger('app')
urllib3.disable_warnings()


@task(name='process_hacks')
def process_hacks():
    logger.info('process_hacks: executed')
    waiting, r = SmwCentral.get_waiting()
    if not waiting:
        logger.debug('No waiting hacks.')
        return 'No waiting hacks.'

    logger.debug('Total Waiting Hacks: {}\n{}'.format(len(waiting), waiting))
    errors = 0
    for h in waiting:
        try:
            logger.debug('text: {}'.format(h.text))
            logger.debug('href: {}'.format(h['href']))
            hack_url = h['href'] if h['href'].startswith('http') else settings.APP_SMWC_URL + h['href']
            logger.debug('hack_url: {}'.format(hack_url))
            query = parse.parse_qs(parse.urlparse(hack_url).query)
            smwc_id = SmwCentral.verify_hack(h, query['id'][0].strip())
            if not smwc_id:
                logging.debug('Unable to verify hack: {}'.format(h.text))
                continue

            logger.debug('smwc_id: {}'.format(smwc_id))
            hack, created = Hacks.objects.get_or_create(smwc_id=smwc_id)
            logger.debug('created: {}'.format(created))
            if created:
                hack.name = h.text
                hack.smwc_href = h['href']
                logger.info('New Hack: {} | {} | {}'.format(hack.smwc_id, hack.name, hack.get_hack_url()))
                statsd.incr('tasks.process_hacks.created')
                SmwCentral.update_hack_info(hack)
                SmwCentral.download_rom(hack)
                hack.save()
                process_alert.delay(hack.pk)
            else:
                logger.debug('Hack Not Created: {}'.format(smwc_id))
        except Exception as error:
            statsd.incr('tasks.process_hacks.errors')
            errors += 1
            logger.exception(error)
            continue
    return 'Processed {} hacks with {} errors.'.format(len(waiting), errors)


@task(name='process_alert')
def process_alert(hack_pk):
    hack = Hacks.objects.get(pk=hack_pk)
    message = 'New Hack: **{}**\nSMWC URL: {}'.format(hack.name, hack.get_hack_url())
    if hack.get_archive_url():
        message += '\nArchive URL: {}'.format(hack.get_archive_url())
    if hack.get_patcher_url():
        short_url = get_short_url(hack.get_patcher_url())
        if short_url:
            logger.debug('short_url: {}'.format(short_url))
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
        logger.debug(message)
    hooks = Webhooks.objects.all()
    if not hooks:
        logger.debug('No hooks found, nothing to do.')
        return
    for hook in hooks:
        if not hook.active:
            continue
        logger.debug('Sending alert to: {}'.format(hook.owner_username))
        send_alert.delay(hook.id, message)


@task(name='send_alert', retry_kwargs={'max_retries': 5, 'countdown': 120})
def send_alert(hook_pk, message):
    try:
        hook = Webhooks.objects.get(pk=hook_pk)
        body = {'content': message}
        r = requests.post(hook.webhook_url, json=body, timeout=30)
        statsd.incr('tasks.send_alert.status_codes.{}'.format(r.status_code))
        if r.status_code == 404:
            logger.warning('Hook {} removed by owner {} - {}'.format(
                hook.hook_id, hook.owner_username, hook.webhook_url))
            hook.delete()
            statsd.incr('tasks.send_alert.hook_delete')
            return '404: Hook removed by owner and deleted from database.'

        if not r.ok:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()

        return '{}: {}'.format(r.status_code, r.content.decode(r.encoding))
    except Exception as error:
        statsd.incr('tasks.send_alert.errors')
        logger.exception(error)
        raise


@task(name='send_discord_message', retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_discord_message(url, message):
    try:
        body = {'content': message}
        r = requests.post(url, json=body, timeout=30)
        statsd.incr('tasks.send_discord_message.status_codes.{}'.format(r.status_code))
        if not r.ok:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()
        return '{}: {}'.format(r.status_code, r.content.decode(r.encoding))

    except Exception as error:
        statsd.incr('tasks.send_discord_message.errors.')
        logger.exception(error)
        raise


class SmwCentral(object):
    @staticmethod
    def get_waiting():
        new_hacks = 'https://www.smwcentral.net/?p=section&s=smwhacks&u=1'
        r = requests.get(new_hacks, timeout=30)
        statsd.incr('tasks.get_waiting.status_codes.{}'.format(r.status_code))
        soup = BeautifulSoup(r.content.decode(r.encoding), 'html.parser')
        search_string = '/\?p=section&a=details&id='
        s = soup.findAll('a', attrs={'href': re.compile(search_string)})
        return s, r

    @staticmethod
    def verify_hack(h, smwc_id):
        if not smwc_id.isdigit():
            logger.error('New hack has non-numeric ID: {}'.format(smwc_id))
            return False
        smwc_id = int(smwc_id)
        if smwc_id < settings.APP_MIN_HACK_ID:
            logger.debug('New hack below min ID: {}'.format(smwc_id))
            return False

        try:
            if h.parent.has_attr('class'):
                if h.parent.attrs['class'][0] == 'rope':
                    logger.debug('New hack parent has class rope: {}'.format(smwc_id))
                    return False
            if h.previous_sibling.startswith('Tip') or h.text == 'Floating IPS':
                logger.debug('New hack detected in as tip: {}'.format(smwc_id))
                return False
            return smwc_id

        except Exception as error:
            logger.debug(error)
            return False

    @staticmethod
    def update_hack_info(hack):
        try:
            logger.info('rom_url: {}'.format(hack.get_hack_url()))
            r = requests.get(hack.get_hack_url(), verify=False, timeout=30)
            statsd.incr('tasks.update_hack_info.status_codes.{}'.format(r.status_code))
            if r.status_code != 200:
                raise Exception('Error retrieving smwc webpage: {}'.format(r.status_code))

            soup = BeautifulSoup(r.content.decode(r.encoding), 'html.parser')
            download = soup.find(string='Download')
            hack.download_url = 'https:{}'.format(download.findPrevious()['href'])

            d = soup.find(string=re.compile('.*Difficulty:.*'))
            hack.difficulty = d.parent.parent.find(class_='cell2').text.strip()

            d = soup.find(string=re.compile('.*Authors:.*'))
            hack.authors = d.parent.parent.find(class_='cell2').text.strip()

            d = soup.find(string=re.compile('.*Length:.*'))
            hack.length = d.parent.parent.find(class_='cell2').text.strip()

            d = soup.find(string=re.compile('.*Description:.*'))
            hack.description = d.parent.parent.find(class_='cell2').text.strip()
            logger.debug(type(hack.description))
            logger.debug('hack.description: {}'.format(hack.description))

            d = soup.find(string=re.compile('.*Demo:.*'))
            demo = d.parent.parent.find(class_='cell2').text.strip()
            hack.demo = True if demo == 'Yes' else False

            d = soup.find(string=re.compile('.*Featured:.*'))
            featured = d.parent.parent.find(class_='cell2').text.strip()
            hack.featured = True if featured == 'Yes' else False

        except Exception as error:
            logger.exception(error)

    @staticmethod
    def download_rom(hack):
        if hack.download_url:
            logger.info('Downloading url: {}'.format(hack.download_url))
            r = requests.get(hack.download_url, verify=False, timeout=30)
            statsd.incr('tasks.download_rom.status_codes.{}'.format(r.status_code))
            if r.status_code != 200:
                logger.error(r.content.decode(r.encoding))
                raise Exception('Error retrieving rom download archive: {}'.format(r.status_code))

            parsed = parse.unquote(os.path.basename(parse.urlparse(hack.download_url).path))
            logger.debug('parsed: {}'.format(parsed))
            name, extension = os.path.splitext(parsed)
            logger.debug('name: {}'.format(name))
            logger.debug('extension: {}'.format(extension))
            slug = slugify(hack.name) if hack.name else slugify(name)
            file_name = '{}-{}{}'.format(slug, hack.smwc_id, extension)
            logger.debug('file_name: {}'.format(file_name))
            year_month = datetime.datetime.now().strftime('%Y/%B')
            file_dir = os.path.join(settings.APP_ROMS_DIR, year_month)
            logger.debug('file_dir: {}'.format(file_dir))
            file_uri = os.path.join(year_month, file_name)
            logger.debug('file_uri: {}'.format(file_uri))
            hack.file_uri = file_uri
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file_path = os.path.join(file_dir, file_name)
            logger.debug('file_path: {}'.format(file_path))
            with open(file_path, 'wb') as f:
                f.write(r.content)
                f.close()
