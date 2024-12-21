import warnings
from pathlib import Path

import environ

env = environ.Env()
# Try to read .env file, if it's not present, assume that application
# is deployed to production and skip reading the file
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    environ.Env.read_env(env_file=env.str('ENV_FILE', default=None))

ROOT_DIR = Path(__file__).parents[1]
APP_DIR = Path(__file__).parent

SECRET_KEY = '1zh$0zlqsd0a_o*4_e)m=%^23yzh#6w_6-6&_f@zd!2+jd&lyl'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = str(ROOT_DIR / "static")
ASSETS_ROOT = ROOT_DIR / "assets"
STATICFILES_DIRS = [
    str(ASSETS_ROOT),
]

MEDIA_ROOT = str(ROOT_DIR / "media")
MEDIA_URL = "/media/"

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django_jinja',
    'menu',  # v2 menu support
    'common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'common.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(APP_DIR / "db.sqlite3"),
    }
}

ROOT_URLCONF = 'common.urls'

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": False,
        'DIRS': [
            str(ROOT_DIR / "templates"),
            str(ASSETS_ROOT / "v2" / "dist" / "img"),  # svg inline support
        ],
        "NAME": "jinja2",
        "OPTIONS": {
            "match_extension": ".jinja2",
            "extensions": [
                "jinja2.ext.do",
                "jinja2.ext.loopcontrols",
                "jinja2.ext.with_",
                "jinja2.ext.i18n",
                "jinja2.ext.autoescape",
                "django_jinja.builtins.extensions.CsrfExtension",
                "django_jinja.builtins.extensions.CacheExtension",
                "django_jinja.builtins.extensions.TimezoneExtension",
                "django_jinja.builtins.extensions.UrlsExtension",
                "django_jinja.builtins.extensions.StaticFilesExtension",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
                "webpack_loader.contrib.jinja2ext.WebpackExtension",
                "common.jinja2_extensions.MessagesExtension",
                "common.jinja2_extensions.MenuExtension",
            ],
            "bytecode_cache": {
                "name": "default",
                "backend": "django_jinja.cache.BytecodeCache",
                "enabled": False,
            },
            "newstyle_gettext": True,
            "autoescape": True,
            "auto_reload": DEBUG,
            "translation_engine": "django.utils.translation",
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'DIRS': [
            str(ROOT_DIR / "templates"),
            str(ROOT_DIR / "assets" / "v2" / "dist" / "img"),
            # svg inline support
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ),
            'debug': DEBUG
        }
    },
]

AUTH_USER_MODEL = "common.User"
LOGOUT_REDIRECT_URL = '/'

WSGI_APPLICATION = 'common.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

WEBPACK_ENVIRONMENT = env.str('WEBPACK_ENVIRONMENT', default="local")
WEBPACK_LOADER = {
    'V1': {
        'BUNDLE_DIR_NAME': f'v1/dist/{WEBPACK_ENVIRONMENT}/',
        # relative to the ASSETS_ROOT
        'STATS_FILE': str(
            ASSETS_ROOT / "v1" / "dist" / WEBPACK_ENVIRONMENT / "webpack-stats-v1.json"),
    },
    'V2': {
        'BUNDLE_DIR_NAME': f'v2/dist/{WEBPACK_ENVIRONMENT}/',
        # relative to the ASSETS_ROOT
        'STATS_FILE': str(
            ASSETS_ROOT / "v2" / "dist" / WEBPACK_ENVIRONMENT / "webpack-stats-v2.json"),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
