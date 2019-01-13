import logging
from django.shortcuts import render

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    return render(request, 'home.html')


def roms_view(request):
    # View: /roms/
    return render(request, 'roms.html')


def error_view(request):
    # View: /error/
    return render(request, 'error.html')


# def success_view(request):
#     # View: /success/
#     return render(request, 'success.html')
