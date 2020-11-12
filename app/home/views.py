import logging
from django.shortcuts import render
from home.models import Hacks

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    return render(request, 'home.html')


def roms_view(request):
    # View: /roms/
    roms = Hacks.objects.all()
    return render(request, 'roms.html', {'roms': roms})
