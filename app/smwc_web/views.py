import logging
from django.http import HttpResponse

logger = logging.getLogger('app')


def health_check(request):
    return HttpResponse('success', status=200)
