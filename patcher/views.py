import logging
import os
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


def show_patcher(request):
    # View: /
    if request.method == 'POST':
        logger.info('POST')
        try:
            form = PatcherForm(request.POST, request.FILES)
            if not form.is_valid():
                return JsonResponse({'error': form.errors}, status=400)
            if form.is_valid():
                logger.info('VALID')
                logger.info(request.FILES['source_rom'])
                logger.info(form.cleaned_data['input_patch'])

                source_rom = request.FILES['source_rom']
                patcher = RomPatcher(source_rom)
                patch_file = patcher.download_rom(form.cleaned_data['input_patch'])
                logger.info('patch_file: {}'.format(patch_file))
                output_file = patcher.patch_rom(patch_file)
                logger.info('output_file: {}'.format(output_file))

                rand = get_random_string()
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, rand))
                fs.base_url += rand + '/'
                filename = fs.save(patcher.patch_name, open(output_file, 'rb'))
                logger.info('filename: {}'.format(filename))
                logger.info('fs.path(filename): {}'.format(fs.path(filename)))
                logger.info('fs.url(filename): {}'.format(fs.url(filename)))

                cleanup_hack.apply_async((os.path.dirname(fs.path(filename)),), countdown=60)

                return JsonResponse({'location': fs.url(filename)})
        except Exception as error:
            logger.exception(error)
            return JsonResponse({'error': error}, status=400)
    else:
        logger.info('GET')
        return render(request, 'patcher.html')
