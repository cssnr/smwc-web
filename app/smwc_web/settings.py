import sentry_sdk
from celery.schedules import crontab
from decouple import config, Csv
from django.contrib.messages import constants as message_constants
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', 'False', bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', '*', Csv())
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', 3600 * 24 * 14, int)

WSGI_APPLICATION = 'smwc_web.wsgi.application'
ROOT_URLCONF = 'smwc_web.urls'
# AUTH_USER_MODEL = 'oauth.CustomUser'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = config('STATIC_ROOT')
MEDIA_ROOT = config('MEDIA_ROOT')
STATICFILES_DIRS = [BASE_DIR / 'static']
TEMPLATES_DIRS = [BASE_DIR / 'templates']

LANGUAGE_CODE = config('LANGUAGE_CODE', 'en-us')
USE_TZ = config('USE_TZ', 'True', bool)
TIME_ZONE = config('TZ', 'UTC')
USE_I18N = True
USE_L10N = True

X_FRAME_OPTIONS = 'SAMEORIGIN'
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', 'False', bool)
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', 'https://*', Csv(delimiter=' '))
SECURE_REFERRER_POLICY = config('SECURE_REFERRER_POLICY', 'no-referrer')
DJANGO_REDIS_IGNORE_EXCEPTIONS = config('REDIS_IGNORE_EXCEPTIONS', True, bool)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', True, bool)

OAUTH_CLIENT_ID = config('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = config('OAUTH_CLIENT_SECRET')
OAUTH_REDIRECT_URI = config('OAUTH_REDIRECT_URI')
OAUTH_SCOPE = config('OAUTH_SCOPE')
OAUTH_RESPONSE_TYPE = 'code'
OAUTH_GRANT_TYPE = 'authorization_code'

CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_TIMEZONE = config('TZ', 'America/Los_Angeles')

STATSD_PREFIX = config('STATSD_PREFIX', 'smwcweb.dev')
STATSD_PORT = config('STATSD_PORT', '8125', int)
STATSD_HOST = config('STATSD_HOST', 'localhost')
# STATSD_CLIENT = config('STATSD_CLIENT', 'django_statsd')

BITLY_ACCESS_TOKEN = config('BITLY_ACCESS_TOKEN')

FTP_HOST = config('FTP_HOST')
FTP_USER = config('FTP_USER')
FTP_PASS = config('FTP_PASS')
FTP_DIR = config('FTP_DIR')
FTP_KEEP_FILES = config('FTP_KEEP_FILES', '10')

APP_ROMS_DIR = config('APP_ROMS_DIR')
APP_TMP_DIR = config('APP_TMP_DIR')
APP_FLIPS_PATH = config('APP_FLIPS_PATH')
APP_SITE_URL = config('APP_SITE_URL').rstrip('/')
APP_STATUS_URL = config('APP_STATUS_URL').rstrip('/')
APP_PATCHER_URL = config('APP_PATCHER_URL').rstrip('/')
APP_ROMS_URL = config('APP_ROMS_URL').rstrip('/')
APP_SMWC_URL = config('APP_SMWC_URL').rstrip('/')
APP_DISCORD_INVITE = config('APP_DISCORD_INVITE')
APP_MIN_HACK_ID = 18000

MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

CELERY_BEAT_SCHEDULE = {
    'process_hacks': {
        'task': 'home.tasks.process_hacks',
        'schedule': crontab('*/10'),
    },
    # 'backup_hacks': {
    #     'task': 'home.tasks.backup_hacks',
    #     'schedule': crontab(minute=5, hour=0),
    # },
}

if config('SENTRY_URL', False):
    sentry_sdk.init(
        dsn=config('SENTRY_URL'),
        environment=config('SENTRY_ENVIRONMENT'),
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        debug=config('SENTRY_DEBUG', False, cast=bool),
    )

CACHES = {
    'default': {
        'BACKEND': config('CACHE_BACKEND',
                          'django.core.cache.backends.dummy.DummyCache'),
        'LOCATION': config('CACHE_LOCATION'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASS'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'OPTIONS': {
            'isolation_level': 'repeatable read',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    },
}

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_extensions',
    'debug_toolbar',
    'home',
    'oauth',
    'patcher',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
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
    # if 'django_statsd.clients.toolbar' in STATSD_CLIENT:
    #     DEBUG_TOOLBAR_PANELS.append('django_statsd.panel.StatsdPanel')
