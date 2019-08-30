from .base import *

ALLOWED_HOSTS = [".dev.compscicenter.ru"]
DEFAULT_URL_SCHEME = 'http'

MEDIA_ROOT = str(Path('/shared', 'media'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_cscdb',
        'USER': 'csc',
        'PASSWORD': 'FooBar',
        'HOST': 'localhost',
        'PORT': ''
    }
}

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
    'LOCATION': '/tmp/django_cache'
}

THUMBNAIL_DEBUG = False

EMAIL_HOST = '127.0.0.1'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Don't use https for staging env
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = '.dev.compscicenter.ru'
CSRF_COOKIE_NAME = "dev_csrf_token"
SESSION_COOKIE_DOMAIN = '.dev.compscicenter.ru'
SESSION_COOKIE_NAME = "dev_cscsessionid"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(ROOT_DIR / "app.log"),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 2,
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['logfile'],
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        },
        "rq.worker": {
            "level": "DEBUG",
            "handlers": ["logfile"],
            'propagate': False,
        },
        "post_office": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400

THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'