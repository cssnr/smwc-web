import logging
import os
from django_statsd.clients import statsd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from patcher.forms import PatcherForm
from patcher.patcher import RomPatcher
from patcher.tasks import cleanup_hack

logger = logging.getLogger('app')
config = settings.CONFIG


def rom_patcher(request):
    # View: /
    if request.method == 'POST':
        try:
            form = PatcherForm(request.POST, request.FILES)
            if not form.is_valid():
                return JsonResponse({'error': form.errors}, status=400)

            if form.is_valid():
                statsd.incr('patcher.rom_patcher.click')
                logger.debug(request.FILES['source_rom'])
                logger.debug('input_patch: {}'.format(form.cleaned_data['input_patch']))
                patcher = RomPatcher(request.FILES['source_rom'])
                if form.cleaned_data['input_patch']:
                    patch_file = patcher.download_rom(form.cleaned_data['input_patch'])
                else:
                    logger.debug(request.FILES['input_file'])
                    patch_file = patcher.write_input_to_file(
                        request.FILES['input_file'], request.FILES['input_file'].name)

                logger.debug('patch_file: {}'.format(patch_file))
                output_file = patcher.patch_rom(patch_file)
                logger.debug('output_file: {}'.format(output_file))
                rand = get_random_string()
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, rand))
                fs.base_url += rand + '/'
                filename = fs.save(patcher.patch_name, open(output_file, 'rb'))
                logger.debug('filename: {}'.format(filename))
                logger.debug('fs.path(filename): {}'.format(fs.path(filename)))
                logger.debug('fs.url(filename): {}'.format(fs.url(filename)))
                cleanup_hack.apply_async((os.path.dirname(fs.path(filename)),), countdown=60)
                statsd.incr('patcher.rom_patcher.success')
                return JsonResponse({'location': fs.url(filename)})

        except Exception as error:
            logger.exception(error)
            statsd.incr('patcher.rom_patcher.error')
            return JsonResponse({'error': error}, status=400)
    else:
        return render(request, 'patcher.html')
