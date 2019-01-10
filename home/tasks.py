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


@task(name='test_task')
def test_task():
    logger.info('test_task: executed')
    return 'test_task: success'


class SmwCentral(object):
    @staticmethod
    def get_rom_info(hack):
        try:
            logger.info('rom_url: {}'.format(hack.hack_url))
            r = requests.get(hack.hack_url, verify=False, timeout=30)
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
        try:
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
                hack.archive_url = '{}/{}'.format(settings.APP_ROMS_URL, file_uri)
        except Exception as error:
            logger.exception(error)

    #  This needs to be its own task...
    @classmethod
    def send_alert(cls, hack):
        message = 'New Hack: **{}**\nSMWC URL: {}'.format(hack.name, hack.hack_url)
        if hack.archive_url:
            message += '\nArchive URL: {}'.format(hack.archive_url)
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
            logger.debug('max_desc: {}'.format(max_desc))
            message += '\n```\n{}\n```'.format(hack.description[:max_desc])
            logger.debug(message)
        hooks = Webhooks.objects.all()
        for hook in hooks:
            if not hook.active:
                continue
            logger.debug('Sending alert to: {}'.format(hook.owner_username))
            r = cls.send_discord(hook.webhook_url, message)
            logger.debug('Result: {}'.format(r.status_code))

    @staticmethod
    def send_discord(url, message):
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


# @task(name='process_hacks')
def process_hacks():
    logger.info('process_hacks: executed')

    waiting, r = SmwCentral.get_waiting()
    if not waiting:
        logger.debug('No new hacks.')
        return

    logger.debug('Total Waiting Hacks: {}\n{}'.format(len(waiting), waiting))
    for h in waiting:
        try:
            hack_url = settings.APP_SMWC_URL + h['href']
            logger.debug('hack_url: {}'.format(hack_url))
            query = urlparse.parse_qs(urlparse.urlparse(hack_url).query)
            smwc_id = query['id'][0].strip()
            try:
                logger.debug('hack_id: {}'.format(smwc_id))
                if smwc_id.isdigit():
                    if int(smwc_id) < settings.APP_MIN_HACK_ID:
                        logger.debug('New hack below min ID: {}'.format(smwc_id))
                        continue
                else:
                    logger.error('New hack has non-numeric ID: "{}" - {}'.format(smwc_id, hack_url))
                    continue
                if h.parent.has_attr('class'):
                    if h.parent.attrs['class'][0] == 'rope':
                        logger.debug('New hack parent has class rope: {}'.format(smwc_id))
                        continue
                if h.previous_sibling.startswith('Tip') or h.text == 'Floating IPS':
                    logger.debug('New hack detected in as tip: {}'.format(smwc_id))
                    continue
            except Exception as error:
                logger.debug(error)
                pass
            hack, created = Hacks.objects.get_or_create(smwc_id=smwc_id, name=h.text, hack_url=hack_url)
            logger.debug('created: {}'.format(created))
            logger.debug(hack)
            if created:
                # logger.debug('----------------------------------------')
                # logger.debug(r.content.decode('iso-8859-1'))
                # logger.debug('----------------------------------------')
                logger.info('New Hack: {} | {} | {}'.format(hack.smwc_id, hack.name, hack.hack_url))
                SmwCentral.get_rom_info(hack)
                SmwCentral.download_rom(hack)
                SmwCentral.send_alert(hack)
                time.sleep(30)
            else:
                logger.debug('Hack Not Created: {}'.format(smwc_id))
        except Exception as error:
            logger.exception(error)
            continue
