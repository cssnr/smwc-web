import logging
import sys
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from patcher.forms import PatcherForm
from patcher.patcher import RomPatcher

logger = logging.getLogger('app')
config = settings.CONFIG


def test_view(request):
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str('test.file')
    response['X-Sendfile'] = smart_str('/tmp/tmp.txt')
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response


def show_patcher(request):
    # View: /
    if request.method == 'POST':
        logger.info('POST')
        form = PatcherForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info('VALID')
            source_rom = request.FILES['source_rom']
            # logger.info(source_rom)
            # raw_file = source_rom.read()
            patcher = RomPatcher(source_rom)
            patch_file = patcher.download_rom(form.cleaned_data['input_patch'])
            patcher.patch_rom(patch_file)

            # response = HttpResponse(data, content_type=mimetypes.guess_type(file_full_path)[0])
            # response['Content-Disposition'] = "attachment; filename={0}".format(filename)
            # response['Content-Length'] = os.path.getsize(file_full_path)
            # return response

            response = HttpResponse(patcher.patch_data, content_type='application/force-download')
            response['Content-Disposition'] = "attachment; filename={0}".format(patcher.patch_name)
            response['Content-Length'] = sys.getsizeof(patcher.patch_data)
            return response

        else:
            logger.info('INVALID')
            return render(request, 'patcher.html')
    else:
        logger.info('GET')
        return render(request, 'patcher.html')
