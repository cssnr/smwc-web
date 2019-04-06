import logging
import os
import tempfile
import re
import requests
import subprocess
import zipfile
from django.utils.text import slugify
from bs4 import BeautifulSoup

logger = logging.getLogger('app')


class RomPatcher(object):
    flips = '/usr/local/bin/flips-linux'
    tempdir_location = '/tmp'
    patch_pattern = '\.(bps|ips)$'
    archive_pattern = '\.(zip)$'

    def __init__(self, source_rom):
        self.TempDir = tempfile.TemporaryDirectory(dir=self.tempdir_location)
        self.tempdir = self.TempDir.name
        self.source_rom = self.write_input_to_file(source_rom, 'smw.sfc')
        self.patch_name = None
        self.output_file = None

    def __repr__(self):
        return 'RomPatcher: {}'.format(self.tempdir)

    def __str__(self):
        return str(self.__repr__)

    def write_input_to_file(self, source_rom, file_name):
        raw_file = source_rom.read()
        file_path = os.path.join(self.tempdir, os.path.basename(file_name))
        with open(file_path, 'wb+') as f:
            f.write(raw_file)
            f.close()
            return file_path

    def download_rom(self, rom_url):
        if not re.search(self.archive_pattern, rom_url, re.IGNORECASE) and \
                not re.search(self.patch_pattern, rom_url, re.IGNORECASE):
            r = requests.get(rom_url, verify=False, timeout=30)
            if not r.ok:
                r.raise_for_status()
            soup = BeautifulSoup(r.content.decode(r.encoding), 'html.parser')
            download = soup.find(string='Download')
            rom_uri = download.findPrevious()['href']
            if not rom_uri:
                error = ('Unable to locate a ROM download at the provided url. '
                         'You can always provide the direct download URL for better results. '
                         'Provuded URL: {}'.format(rom_url))
                raise ValueError(error)
            rom_url = 'https:{}'.format(rom_uri)

        r = requests.get(rom_url, verify=False, timeout=30)
        if not r.ok:
            r.raise_for_status()

        patch_file = os.path.join(self.tempdir, os.path.basename(rom_url))
        with open(patch_file, 'wb+') as f:
            f.write(r.content)
            f.close()
        return patch_file

    def patch_rom(self, patch_file, source_ext):
        if re.search(self.archive_pattern, patch_file, re.IGNORECASE):
            archive = zipfile.ZipFile(patch_file)
            archive.extractall(self.tempdir)
            archive.close()
            patch_file = self.find_first_file(self.tempdir, self.patch_pattern)

        file_name = slugify(os.path.basename(re.split(self.patch_pattern, patch_file)[0]))
        logger.info('file_name: {}'.format(file_name))
        self.patch_name = '{}.{}'.format(file_name, source_ext.lstrip('.'))
        logger.info('self.patch_name: {}'.format(self.patch_name))
        self.output_file = os.path.join(self.tempdir, os.path.basename(self.patch_name))
        logger.info('self.output_file: {}'.format(self.output_file))

        patch_command = [
            self.flips, '--apply', patch_file, self.source_rom, self.output_file
        ]
        if source_ext.lower() != '.smc':
            patch_command.insert(1, '--exact')
        call = subprocess.check_call(patch_command)
        logger.info('call: {}'.format(call))
        return self.output_file

    @staticmethod
    def find_first_file(directory, pattern):
        for root, subdirs, files in os.walk(directory):
            for f in files:
                if re.search(pattern, f):
                    return os.path.join(root, f)
