import logging
from django.shortcuts import render

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    return render(request, 'home.html')


def success_view(request):
    # View: /success/
    return render(request, 'success.html')


def error_view(request):
    # View: /error/
    return render(request, 'error.html')
