import os
from celery.schedules import crontab
from distutils.util import strtobool

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = 'smwc_web.urls'
WSGI_APPLICATION = 'smwc_web.wsgi.application'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMPLATES_DIRS = [os.path.join(BASE_DIR, 'templates')]

SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 3600 * 24 * 14))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(' ')
DEBUG = strtobool(os.getenv('DEBUG', 'False'))
SECRET_KEY = os.environ['SECRET_KEY']
STATIC_ROOT = os.environ['STATIC_ROOT']
MEDIA_ROOT = os.environ['MEDIA_ROOT']

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
DATETIME_FORMAT = os.getenv('DATETIME_FORMAT', 'N j, Y, f A')
TIME_ZONE = os.getenv('TZ', 'America/Los_Angeles')
USE_TZ = strtobool(os.getenv('USE_TZ', 'True'))

USE_I18N = True
USE_L10N = True

USE_X_FORWARDED_HOST = strtobool(os.getenv('USE_X_FORWARDED_HOST', 'False'))
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'no-referrer')
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI')
OAUTH_SCOPE = os.getenv('OAUTH_SCOPE')
OAUTH_RESPONSE_TYPE = 'code'
OAUTH_GRANT_TYPE = 'authorization_code'

CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
CELERY_TIMEZONE = os.getenv('TZ', 'America/Los_Angeles')

STATSD_PREFIX = os.getenv('STATSD_PREFIX', 'smwcweb.dev')
STATSD_PORT = int(os.getenv('STATSD_PORT', '8125'))
STATSD_HOST = os.getenv('STATSD_HOST', 'localhost')
STATSD_CLIENT = os.getenv('STATSD_CLIENT', 'django_statsd.clients.normal')

BITLY_ACCESS_TOKEN = os.environ['BITLY_ACCESS_TOKEN']

FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
FTP_DIR = os.getenv('FTP_DIR')
FTP_KEEP_FILES = os.getenv('FTP_KEEP_FILES', '10')

APP_ROMS_DIR = os.environ['APP_ROMS_DIR']
APP_TMP_DIR = os.environ['APP_TMP_DIR']
APP_FLIPS_PATH = os.environ['APP_FLIPS_PATH']
APP_SITE_URL = os.environ['APP_SITE_URL'].rstrip('/')
APP_STATUS_URL = os.environ['APP_STATUS_URL'].rstrip('/')
APP_PATCHER_URL = os.environ['APP_PATCHER_URL'].rstrip('/')
APP_ROMS_URL = os.environ['APP_ROMS_URL'].rstrip('/')
APP_SMWC_URL = os.environ['APP_SMWC_URL'].rstrip('/')
APP_DISCORD_INVITE = os.environ['APP_DISCORD_INVITE']
APP_MIN_HACK_ID = 18000

CELERY_BEAT_SCHEDULE = {
    'process_hacks': {
        'task': 'home.tasks.process_hacks',
        'schedule': crontab('*/10'),
    },
    'backup_hacks': {
        'task': 'home.tasks.backup_hacks',
        'schedule': crontab(minute=5, hour=0),
    },
}

CACHES = {
    'default': {
        'BACKEND': os.getenv('CACHE_BACKEND',
                             'django.core.cache.backends.locmem.LocMemCache'),
        'LOCATION': os.getenv('CACHE_LOCATION', 'memcached:11211'),
        'OPTIONS': {
            'server_max_value_length': 1024 * 1024 * 4,
        }
    }
}

if DEBUG:
    def show_toolbar(request):
        return True if request.user.is_staff else False
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_toolbar}
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
    if 'django_statsd.clients.toolbar' in STATSD_CLIENT:
        DEBUG_TOOLBAR_PANELS.append('django_statsd.panel.StatsdPanel')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASS'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
        'OPTIONS': {
            'isolation_level': 'repeatable read',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('%(asctime)s - '
                       '%(levelname)s - '
                       '%(filename)s '
                       '%(module)s.%(funcName)s:%(lineno)d - '
                       '%(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': os.getenv('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_extensions',
    'django_statsd',
    'debug_toolbar',
    'home',
    'oauth',
    'patcher',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]
