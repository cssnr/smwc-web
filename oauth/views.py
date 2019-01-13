import logging
import random
import requests
import string
import urllib.parse
from django_statsd.clients import statsd
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pprint import pformat
from home.models import Webhooks
from home.tasks import send_discord_message

logger = logging.getLogger('app')


def do_oauth(request):
    """
    # View  /oauth/
    """
    request.session['state'] = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(20))
    params = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'scope': settings.OAUTH_SCOPE,
        'response_type': settings.OAUTH_RESPONSE_TYPE,
        'state': request.session['state'],
    }
    url_params = urllib.parse.urlencode(params)
    url = 'https://discordapp.com/api/oauth2/authorize?{}'.format(url_params)
    logger.debug('url: {}'.format(url))
    statsd.incr('oauth.do_oauth.click')
    return HttpResponseRedirect(url)


def callback(request):
    """
    # View  /oauth/callback/
    """
    try:
        oauth_state = request.GET['state']
        if oauth_state != request.session['state']:
            logger.warning('STATE DOES NOT MATCH: {}'.format(oauth_state))
        oauth_code = request.GET['code']
        logger.info('oauth_code: {}'.format(oauth_code))
        oauth_response = oauth_token(oauth_code)
        logger.info(pformat(oauth_response))
        discord_profile = get_discord(oauth_response['access_token'])
        logger.info(pformat(discord_profile))
        webhook = Webhooks(
            owner_username=discord_profile['username'],
            webhook_url=oauth_response['webhook']['url'],
            hook_id=oauth_response['webhook']['id'],
            guild_id=oauth_response['webhook']['guild_id'],
            channel_id=oauth_response['webhook']['channel_id'],
        )
        webhook.save()
        success_message = ('Webhook successfully added. '
                           'New rom-hacks will show up here as they are posted. '
                           'To browse the archive visit: {}').format(settings.APP_ROMS_URL)
        send_discord_message.delay(oauth_response['webhook']['url'], success_message)
        statsd.incr('oauth.callback.success.')
        message(request, 'success', 'Operation Successful!')
        return redirect('home:index')
    except Exception as error:
        statsd.incr('oauth.callback.errors.')
        logger.exception(error)
        message(request, 'danger', 'Fatal Login Auth. Report as Bug.')
        return redirect('home:index')


@require_http_methods(['POST'])
def log_out(request):
    """
    View  /oauth/logout/
    """
    logout(request)
    message(request, 'success', 'You have logged out.')
    return redirect('home:index')


def oauth_token(code):
    """
    Get access_token from code
    """
    url = 'https://discordapp.com/api/oauth2/token'
    data = {
        'client_id': settings.OAUTH_CLIENT_ID,
        'client_secret': settings.OAUTH_CLIENT_SECRET,
        'grant_type': settings.OAUTH_GRANT_TYPE,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'code': code,
        'scope': settings.OAUTH_SCOPE,
    }
    r = requests.post(url, data=data, timeout=10)
    statsd.incr('oauth.oauth_token.status_codes.{}'.format(r.status_code))
    logger.debug('status_code: {}'.format(r.status_code))
    logger.debug('content: {}'.format(r.content))
    return r.json()


def get_discord(access_token):
    """
    Get profile for authorized user
    """
    url = 'https://discordapp.com/api/users/@me'
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }
    r = requests.get(url, headers=headers, timeout=10)
    statsd.incr('oauth.get_discord.status_codes.{}'.format(r.status_code))
    logger.debug('status_code: {}'.format(r.status_code))
    logger.debug('content: {}'.format(r.content))
    return r.json()


def message(request, level, message):
    """
    Easily add a success or error message
    """
    if level == 'success':
        messages.add_message(request, messages.SUCCESS, message, extra_tags='success')
    else:
        messages.add_message(request, messages.WARNING, message, extra_tags=level)
