from __future__ import absolute_import, unicode_literals
import datetime
import logging
import os
import re
import requests
import time
import urllib.parse as urlparse
from django.conf import settings
from bs4 import BeautifulSoup
from celery import task
from home.models import Hacks, Webhooks

logger = logging.getLogger('app')


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
            query = urlparse.parse_qs(urlparse.urlparse(hack_url).query)
            smwc_id = SmwCentral.verify_hack(h, query['id'][0].strip())
            if not smwc_id:
                logging.debug('Unable to verify hack: {}'.format(h.text))
                continue

            hack, created = Hacks.objects.get_or_create(smwc_id=smwc_id, name=h.text, smwc_href=h['href'])
            logger.debug('created: {}'.format(created))
            if created:
                logger.info('New Hack: {} | {} | {}'.format(hack.smwc_id, hack.name, hack.get_hack_url()))
                SmwCentral.update_hack_info(hack)
                SmwCentral.download_rom(hack)
                SmwCentral.send_alert(hack)
                hack.save()
            else:
                logger.debug('Hack Not Created: {}'.format(smwc_id))
            logger.debug('-- waiting loop finished  --')
            # time.sleep(5)
        except Exception as error:
            errors += 1
            logger.exception(error)
            continue
    return 'Processed {} hacks with {} errors.'.format(len(waiting), errors)


class SmwCentral(object):
    #  This needs to be its own task...
    @classmethod
    def send_alert(cls, hack):
        message = 'New Hack: **{}**\nSMWC URL: {}'.format(hack.name, hack.get_hack_url())
        if hack.get_archive_url():
            message += '\nArchive URL: {}'.format(hack.get_archive_url())
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
            r = cls._send_discord(hook.webhook_url, message)
            logger.debug('Result: {}'.format(r.status_code))
            logger.debug('-- hooks loop finished - sleep 5')
            time.sleep(5)

    @staticmethod
    def _send_discord(url, message):
        try:
            body = {'content': message}
            return requests.post(url, json=body, timeout=15)
        except Exception as error:
            logger.exception(error)
            return False

    @staticmethod
    def get_waiting():
        new_hacks = 'https://www.smwcentral.net/?p=section&s=smwhacks&u=1'
        r = requests.get(new_hacks, timeout=30)
        soup = BeautifulSoup(r.content.decode('iso-8859-1'), 'html.parser')
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
            if r.status_code != 200:
                raise Exception('Error retrieving smwc webpage: {}'.format(r.status_code))
            soup = BeautifulSoup(r.content.decode('iso-8859-1'), 'html.parser')
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
            if r.status_code != 200:
                raise Exception('Error retrieving rom download archive: {}'.format(r.status_code))
            rom_file_name = os.path.basename(hack.download_url).replace('%20', '_')
            file_name = '{}-{}'.format(hack.smwc_id, rom_file_name)
            logger.debug('file_name: {}'.format(file_name))
            year_month = datetime.datetime.now().strftime('%Y/%B')
            file_dir = os.path.join(settings.APP_ROMS_DIR, year_month)
            logger.debug('file_dir: {}'.format(file_dir))
            file_uri = os.path.join(year_month, file_name)
            logger.debug('file_uri: {}'.format(file_uri))
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file_path = os.path.join(file_dir, file_name)
            logger.debug('file_path: {}'.format(file_path))
            with open(file_path, 'wb') as f:
                f.write(r.content)
                f.close()
            hack.file_uri = file_uri
