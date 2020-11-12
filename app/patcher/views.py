import logging
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django_statsd.clients import statsd
from patcher.forms import PatcherForm
from patcher.patcher import RomPatcher
from patcher.tasks import cleanup_hack

logger = logging.getLogger('app')


def patcher_view(request):
    # View: /patcher/
    if request.method == 'GET':
        return render(request, 'patcher.html')

    try:
        form = PatcherForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({'error': form.errors}, status=400)

        statsd.incr('patcher.rom_patcher.click')
        patcher = RomPatcher()

        # 2 - SOURCE ROM
        if form.cleaned_data['source_file']:
            # 2b - source FILE provided
            logger.debug(request.FILES['source_file'])
            patcher.source_ext = patcher.get_file_extension(request.FILES['source_file'].name)
            patcher.source_rom_path = patcher.write_input_to_file(
                request.FILES['source_file'], 'smw{}'.format(patcher.source_ext)
            )
        else:
            # 2a - source URL provided
            logger.debug(form.cleaned_data['source_url'])
            patcher.source_ext = patcher.get_file_extension(form.cleaned_data['source_url'])
            patcher.source_rom_path = patcher.download_url_to_file(
                form.cleaned_data['source_url'], 'smw{}'.format(patcher.source_ext)
            )
        logger.debug('patcher.source_rom_path: {}'.format(patcher.source_rom_path))

        # 1 - PATCH FILE
        if form.cleaned_data['patch_file']:
            # 1a - patch FILE provided
            logger.debug(request.FILES['patch_file'])
            patcher.patch_file = patcher.write_input_to_file(
                request.FILES['patch_file'], request.FILES['patch_file'].name
            )
        else:
            # 1b - patch URL provided
            logger.debug(form.cleaned_data['patch_url'])
            patcher.patch_file = patcher.download_rom(form.cleaned_data['patch_url'])
        logger.debug('patcher.patch_file: {}'.format(patcher.patch_file))

        new_rom_path = patcher.patch_rom(patcher.patch_file, patcher.source_ext)
        logger.debug('new_rom_path: {}'.format(new_rom_path))
        logger.debug('patcher.new_rom_path: {}'.format(patcher.new_rom_path))
        logger.debug('patcher.new_rom_name: {}'.format(patcher.new_rom_name))

        rand = get_random_string()
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, rand))
        fs.base_url += rand + '/'

        filename = fs.save(patcher.new_rom_name, open(patcher.new_rom_path, 'rb'))
        logger.debug('filename: {}'.format(filename))
        logger.debug('fs.path(filename): {}'.format(fs.path(filename)))
        logger.debug('fs.url(filename): {}'.format(fs.url(filename)))
        cleanup_hack.apply_async((os.path.dirname(fs.path(filename)),), countdown=120)

        statsd.incr('patcher.rom_patcher.success')
        return JsonResponse({'location': fs.url(filename)})

    except Exception as error:
        logger.exception(error)
        statsd.incr('patcher.rom_patcher.error')
        return JsonResponse({'error': error}, status=400)
