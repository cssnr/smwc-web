import logging
from django.conf import settings
from django.shortcuts import render, redirect
from home.models import Hacks

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    return render(request, 'home.html')


def join_discord(request):
    # View: /discord/
    return redirect(settings.APP_DISCORD_INVITE)


def roms_view(request):
    # View: /roms/
    roms = Hacks.objects.all()
    return render(request, 'roms.html', {'roms': roms})
