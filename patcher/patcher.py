import logging
import os
import tempfile
import re
import requests
import subprocess
import zipfile
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
        self.source_rom = self.write_source_to_file(source_rom)
        self.patch_name = None
        self.patch_data = None

    def __repr__(self):
        return 'RomPatcher: {}'.format(self.tempdir)

    def __str__(self):
        return str(self.__repr__)

    def write_source_to_file(self, source_rom):
        raw_file = source_rom.read()
        file_path = os.path.join(self.tempdir, os.path.basename('smw.sfc'))
        with open(file_path, 'wb') as f:
            f.write(raw_file)
            f.close()
            del raw_file, source_rom
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
        with open(patch_file, 'wb') as f:
            f.write(r.content)
            f.close()
        return patch_file

    def patch_rom(self, patch_file):
        if re.search(self.archive_pattern, patch_file, re.IGNORECASE):
            archive = zipfile.ZipFile(patch_file)
            archive.extractall(self.tempdir)
            archive.close()
            patch_file = self.find_first_file(self.tempdir, self.patch_pattern)

        file_name = re.split(self.patch_pattern, patch_file)[0].replace(' ', '_')
        logger.info('file_name: {}'.format(file_name))
        self.patch_name = '{}.sfc'.format(os.path.basename(file_name))
        logger.info('self.patch_name: {}'.format(self.patch_name))
        output_file = os.path.join(self.tempdir, os.path.basename(self.patch_name))
        logger.info('output_file: {}'.format(output_file))

        patch_command = [
            os.path.join(self.flips), '--apply', '--exact',
            patch_file, self.source_rom, output_file,
        ]
        subprocess.check_call(patch_command)
        with open(output_file, 'rb') as f:
            self.patch_data = f.read()
            self.TempDir.cleanup()

    @staticmethod
    def find_first_file(directory, pattern):
        for root, subdirs, files in os.walk(directory):
            for f in files:
                if re.search(pattern, f):
                    return os.path.join(root, f)
