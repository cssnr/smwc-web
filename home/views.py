import logging
from django.shortcuts import render, HttpResponse
from home.tasks import test_task

logger = logging.getLogger('app')


def test_view(request):
    # View: /testing/
    test_task.delay()
    return HttpResponse('yes')


def home_view(request):
    # View: /
    return render(request, 'home.html')


def success_view(request):
    # View: /success/
    return render(request, 'success.html')


def error_view(request):
    # View: /error/
    return render(request, 'error.html')
