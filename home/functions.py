import requests
from django.conf import settings


def get_short_url(long_url, title=None, tags=None, domain=None):
    url = 'https://api-ssl.bitly.com/v4/bitlinks'
    headers = {
        'Authorization': 'Bearer {}'.format(settings.BITLY_ACCESS_TOKEN),
        'Content-Type': 'application/json',
    }
    data = {'long_url': long_url}
    if title:
        data['title'] = title
    if title:
        data['tags'] = tags
    if title:
        data['domain'] = domain
    r = requests.post(url, json=data, headers=headers, timeout=10)
    if r.ok:
        return r.json()['link']
    else:
        return None
