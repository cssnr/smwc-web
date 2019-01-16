import logging
import json
import requests
import time
from datetime import datetime
from django.conf import settings

logger = logging.getLogger('app')
config = settings.CONFIG

CLIENT_ID = 'micl15dobqhfs7xbfpvlnzdpt3kt12d'  # twitch client-id
PB_API_KEY = 'e1e2b7f04fc80d7eedee48bf3d33a2ea'  # pastebin api key
API_RATE_LIMIT = .5
MAX_CHATTERS = 500

KNOWN_BOT_LIST = [
    'analyticsbot',
    'apricotdrupefruit',
    'boomtvmod',
    'buttsbot',
    'commanderroot',
    'electricallongboard',
    'electricalskateboard',
    'extrafirmbot',
    'faegwent',
    'hnlbot',
    'logviewer',
    'moobot',
    'mtgbot',
    'muxybot',
    'nightbot',
    'p0sitivitybot',
    'sc2replaystatsbot',
    'slocool',
    'smashedbott',
    'squadbott',
    'streamelements',
    'stay_hydrated_bot',
    'super_happy_bot',
    'v_and_k',
    'vivbot',
    'wizebot',
    'xanbot',
]

LINKS = {
    'Logviewer': 'https://cbenni.com/{0}',
    'Skully Gnome': 'https://sullygnome.com/channel/{0}',
    'Socialblade': 'https://socialblade.com/twitch/user/{0}',
    'Stream Elements': 'https://stats.streamelements.com/c/{0}',
    'Twinge': 'http://twinge.tv/channels/{0}',
    'Twitch Stats': 'https://twitchstats.net/streamer/{0}',
    'Twitch Tools': 'https://www.twitchtools.com/channel/{0}',
}


def req_twitch_json(uri):
    h = {'Client-ID': CLIENT_ID}
    r = requests.get(uri, headers=h)
    j = json.loads(r.text)
    return j


def convert_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h < 1:
        o = "%02d minutes %02d seconds" % (m, s)
    else:
        o = "%d hours %02d minutes %02d seconds" % (h, m, s)
    return o


def send_pastebin(name, paste, expire='N'):
    """
    https://pastebin.com/api
    """
    uri = 'https://pastebin.com/api/api_post.php'
    d = {
        'api_paste_name': name,
        'api_paste_code': paste,
        'api_dev_key': PB_API_KEY,
        'api_option': 'paste',
        'api_paste_private': 0,
        'api_paste_expire_date': expire,
    }
    r = requests.post(uri, data=d)
    result = r.content.decode("utf-8")
    if 'Bad API request' in result:
        return 'Pastebin API Error: %s' % result
    else:
        paste_key = result.split('.com/')[1]
        return 'https://pastebin.com/raw/%s' % paste_key


def live_channel_stats(channel, chatters=True):
    CHANNEL = channel
    PROCESS_CHATTERS = chatters
    results = {'success': False, 'data': None}

    chatters_url = 'http://tmi.twitch.tv/group/user/%s/chatters' % CHANNEL.lower()
    chatters_json = req_twitch_json(chatters_url)

    moderator_list = chatters_json['chatters']['moderators']
    chatter_list = chatters_json['chatters']['viewers']
    chatter_count = chatters_json['chatter_count']
    all_chatters = chatter_list + moderator_list

    channel_url = 'https://api.twitch.tv/kraken/channels/%s' % CHANNEL
    channel_json = req_twitch_json(channel_url)
    time.sleep(API_RATE_LIMIT)
    stream_url = 'https://api.twitch.tv/kraken/streams/%s' % CHANNEL
    stream_json = req_twitch_json(stream_url)

    if not stream_json['stream']:
        results['data'] = 'Stream Offline'
        return results

    created_at = stream_json['stream']['created_at']
    stream_created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    stream_uptime = datetime.utcnow() - stream_created_date
    uptime = convert_time(stream_uptime.seconds)

    is_partner = 'Yes' if channel_json['partner'] else 'No'
    is_live = 'Yes' if stream_json['stream']['stream_type'] == 'live' else 'No'

    channel_info = (
        'Channel:            {}\n'
        'Display Name:       {}\n'
        'User ID:            {}\n'
        'Twitch Partner:     {}\n'
        'Current Time:       {}\n'
        'Channel Created:    {}\n'
        'Stream Started:     {}\n'
        'Stream Uptime:      {}\n'
        'Live Stream:        {}\n'
        'Title:              {}\n'
        'Game:               {}\n'
        'Resolution:         {}p @ {}fps\n'
        'Total Views:        {}\n'
        'Followers:          {}\n'
        'Viewers:            {}\n'
        'Chatter Count:      {}\n'
    ).format(
        CHANNEL,
        channel_json['display_name'],
        channel_json['_id'],
        is_partner,
        datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        channel_json['created_at'],
        created_at,
        uptime,
        is_live,
        channel_json['status'],
        stream_json['stream']['game'],
        stream_json['stream']['video_height'],
        round(stream_json['stream']['average_fps']),
        channel_json['views'],
        channel_json['followers'],
        stream_json['stream']['viewers'],
        chatter_count,
    )

    # all_data = '%s\n' % channel_info
    results['data'] = channel_info + '\n'

    logger.info('%s chatters for %s', chatter_count, CHANNEL)

    if chatter_count > MAX_CHATTERS or not PROCESS_CHATTERS:
        results['success'] = True
        return results

    viewer_list = []

    for viewer in all_chatters:
        try:
            viewer_uri = 'https://api.twitch.tv/kraken/users/%s' % viewer
            time.sleep(API_RATE_LIMIT)
            following_json = req_twitch_json(viewer_uri)
            try:
                created_at = following_json['created_at']
                out = '%s     %s' % (created_at, viewer)
            except Exception:
                created_at = '1999-01-01T00:00:00Z'
                out = '%s     %s (UNKNOWN)' % (created_at, viewer)

            if viewer in moderator_list:
                out = '%s (mod)' % out
            if viewer in KNOWN_BOT_LIST:
                out = '%s (bot)' % out
            viewer_list.append(out)
        except Exception:
            continue

    try:
        viewer_list.sort(
            key=lambda x: datetime.strptime(x.split(' ')[0], '%Y-%m-%dT%H:%M:%SZ')
        )
        viewer_list = reversed(viewer_list)
    except Exception as error:
        logger.exception(error)

    section_heading = (
        'created_at               username\n'
        '--------------------     --------------------'
    )
    results['data'] += '%s\n' % section_heading
    all_viewers = ''

    for viewer_info in viewer_list:
        all_viewers += '%s\n' % viewer_info

    results['data'] += all_viewers
    results['success'] = True
    return results

    # if UPLOAD_PASTEBIN:
    #     p = send_pastebin('%s Twitch Channel Info'.format(CHANNEL), all_data)
    #     print(p)


AGDQ_LIST = [
    'Vysuals',
    'swordsmankirby',
    'V0oid',
    'Fathlo23',
    'stew_',
    'Keverage',
    'Krankdud',
    'popesquidward',
    'alexh0we',
    'ConnorAce',
    'Tyler2022',
    'ChurchNEOH',
    'RagnellGoW',
    'Puncayshun',
    'CorundumCore',
    'SecksWrecks',
    'MrUppercaseT',
    'MrCab',
    'snapcase',
    'Brandooates',
    'Konasumi',
    'Cyclone',
    'd4gr0n',
    'chronoon',
    'Nubzombie',
    'RottDawg',
    'd4gr0n',
    'NME',
    'PJ',
    'Satoryu',
    'VB__',
    'lurk',
    'jc583',
    'Laxxus',
    'Kruncha',
    'michael_goldfish',
    'spikevegeta2',
    'ThaRixer',
    'TonesBalones',
    'RawDerps',
    'Punchy',
    'SmoothOperative',
    'PlasticRainbow',
    'Fullest',
    'Karma',
    'Toad22484',
    'RottDawg',
    'garadas21',
    'swordsmankirby',
    'garadas21',
    'LackAttack24',
    'Glackum',
    'Primorix',
    'Revolucion',
    'thebluemania',
    'Gyoo',
    'Kirbymastah',
    'abney317',
    'mitchflowerpower',
    'Gadien',
    'Jabem',
    'Arobam',
    'TrjnRabbit',
    'ThePackle',
    'ThePackle',
    'Archariat',
    'Brandooates',
    'altabiscuit',
    'FuzzyGames',
    'halfcoordinated',
    'AND4H',
    'Krankdud',
    'CovertMuffin',
    'Copitz',
    'Swoodeasu',
    'WoLfy',
    'Pedrogas',
    'SkyBlueAether',
    'Trogdor',
    'Calebhart42',
    'ColonelFatso',
    'Tokyo90',
    'Walrus_Prime',
    'Soppa',
    'Madu',
    'usedpizza',
    'EndySWE',
    'Lizstar',
    'Gyre',
    'PeteDorr',
    'janglestorm',
    'PJ',
    'saintmillion',
    'sharif',
    'NPC',
    'GarbitheGlitcheress',
    'Iceplug',
    'coolkid',
    'Brossentia',
    'ZakkyTheShimmeringKirin',
    'Eriphram',
    'miniomegaking',
    'just_defend',
    'SpootyBiscuit',
    'bloodthunder',
    'Metro72',
    'KingDime',
    'KingDime',
    'Graviton',
    'peaches',
    'SpootyBiscuit',
    'strizer86',
    'Studio',
    'ChurchnSarge',
    'TGH',
    'Linkus7',
    'Pinballwiz45b',
    'Trob',
    'GoatPuncherArctic',
    'CScottyW',
    'MrLlamaSC',
    'Semanari',
    'KZ_FREW',
    'Gunnermaniac3',
    'pokeguy84',
    'Neerrm',
    'riversmccown',
    'Khobahi',
    'Obdajr',
    'dwangoAC',
    'dwangoAC',
    'PangaeaPanga',
    'SniperKing',
    'Tojju',
    'Muttski',
    'Luzbelheim',
    'Scottobozo',
    'usedpizza',
    'BBF',
    'Xelna',
    'spacey1',
    'GlitchCat7',
    'RBMACHOK',
    'Dode',
    'Wahnthac',
    'Bayleef',
    'ShinyZeni',
]


def agdq():
    results = {'success': False, 'data': None}
    online = []
    for g in AGDQ_LIST:
        time.sleep(API_RATE_LIMIT)
        stream_url = 'https://api.twitch.tv/kraken/streams/%s' % g
        stream_json = req_twitch_json(stream_url)
        if 'stream' in stream_json:
            if stream_json['stream']:
                o = '{} - {} - {}'.format(g, stream_json['stream']['viewers'],
                                          stream_json['stream']['game'])
                online.append(o)
        else:
            logger.info('Unknown:  {}'.format(g))

    results['data'] = '{} - GDQ Streamers Online\n\n'.format(len(online))
    for x in online:
        results['data'] += x + '\n'
    results['success'] = True
    return results
