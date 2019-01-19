import ast
import os
from celery.schedules import crontab
from configparser import ConfigParser
from distutils.util import strtobool

settings_file = 'settings.ini'

ROOT_URLCONF = 'smwc_web.urls'
WSGI_APPLICATION = 'smwc_web.wsgi.application'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = ConfigParser()
CONFIG.read(os.path.join(BASE_DIR, settings_file))

LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
LOGIN_REDIRECT_URL = '/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMPLATES_DIRS = [os.path.join(BASE_DIR, 'templates')]

ALLOWED_HOSTS = CONFIG['django']['allowed_hosts'].split(' ')
DEBUG = strtobool(CONFIG['django']['debug'])
SECRET_KEY = CONFIG['django']['secret']
STATIC_ROOT = CONFIG['django']['static_root']
MEDIA_ROOT = CONFIG['django']['media_root']

LANGUAGE_CODE = CONFIG['django']['language_code']
TIME_ZONE = CONFIG['django']['time_zone']

USE_I18N = True
USE_L10N = True
USE_TZ = True

APP_ROMS_DIR = CONFIG['app']['roms_dir']
APP_SITE_URL = CONFIG['app']['site_url']
APP_ROMS_URL = CONFIG['app']['roms_url']
APP_SMWC_URL = CONFIG['app']['smwc_url']
APP_MIN_HACK_ID = int(CONFIG['app']['min_hack_id'])
APP_DISCORD_INVITE = CONFIG['app']['discord_invite']

OAUTH_CLIENT_ID = CONFIG['oauth']['client_id']
OAUTH_CLIENT_SECRET = CONFIG['oauth']['client_secret']
OAUTH_REDIRECT_URI = CONFIG['oauth']['redirect_uri']
OAUTH_RESPONSE_TYPE = CONFIG['oauth']['response_type']
OAUTH_GRANT_TYPE = CONFIG['oauth']['grant_type']
OAUTH_SCOPE = CONFIG['oauth']['scope'].strip('"')

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = CONFIG['django']['time_zone']
CELERY_BEAT_SCHEDULE = {
    'every-ten-minutes': {
        'task': 'process_hacks',
        'schedule': crontab('*/10'),
    },
}

STATSD_PREFIX = CONFIG.get('statsd', 'metric_prefix', fallback='smwcweb.dev')
STATSD_PORT = CONFIG.getint('statsd', 'metric_port', fallback=8125)
STATSD_HOST = CONFIG.get('statsd', 'metric_host', fallback='localhost')
STATSD_CLIENT = CONFIG.get('statsd', 'metric_client', fallback='django_statsd.clients.toolbar')


if DEBUG:
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

    def show_toolbar(request):
        return True if request.user.is_staff else False

    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_toolbar}

if 'sqlite_db' in CONFIG['django']:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': CONFIG['database']['name'],
            'USER': CONFIG['database']['user'],
            'PASSWORD': CONFIG['database']['pass'],
            'HOST': CONFIG['database']['host'],
            'PORT': CONFIG['database']['port'],
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('%(asctime)s - %(levelname)s '
                       '%(module)s.%(funcName)s:%(lineno)d - '
                       '%(message)s')
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': CONFIG['logging']['log_file'],
            'formatter': 'standard',
            'maxBytes': 1024 * 1024 * 10,  # 100 mb
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': [CONFIG['logging']['django_handler']],
            'level': CONFIG['logging']['django_level'],
            'propagate': True,
        },
        'app': {
            'handlers': [CONFIG['logging']['app_handler']],
            'level': CONFIG['logging']['app_level'],
            'propagate': True,
        },
        # 'celery': {
        #     'handlers': [CONFIG['logging']['app_handler']],
        #     'level': [CONFIG['logging']['app_handler']],
        #     'filename': 'celery.log',
        #     'formatter': 'simple',
        # },
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
    'oauth',
    'home',
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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
