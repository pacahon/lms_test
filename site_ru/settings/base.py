# Read project environment into os.environ before importing base configuration
import sys
import warnings

import environ

env = environ.Env()
# Try to read .env file, if it's not present, assume that application
# is deployed to production and skip reading the file
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    environ.Env.read_env(env_file=env.str('ENV_FILE', default=None))

from lms.settings.extended import *

sys.path.append(str(Path(__file__).parents[1] / "apps"))

SITE_ID = 1
if REDIS_DB_INDEX is None:
    for queue_config in RQ_QUEUES.values():
        queue_config['DB'] = SITE_ID
    THUMBNAIL_REDIS_DB = SITE_ID

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["lk.yandexdataschool.ru"])

WSGI_APPLICATION = 'site_ru.wsgi.application'
ROOT_URLCONF = 'site_ru.urls'
LMS_SUBDOMAIN = None
LMS_DOMAIN = 'lk.yandexdataschool.ru'
LMS_CURATOR_EMAIL = 'shadcurators@yandex.ru'
LMS_MENU = 'site_ru.menu'
if YANDEX_METRIKA_ID is None:
    YANDEX_METRIKA_ID = 75819112
SUBDOMAIN_URLCONFS = {
    None: ROOT_URLCONF,
}

INSTALLED_APPS += [
    'application.apps.ApplicationConfig'
]

ESTABLISHED = 2007
DEFAULT_CITY_CODE = "msk"
DEFAULT_BRANCH_CODE = "msk"

# Template customization
FAVICON_PATH = 'v1/img/shad/favicon.ico'
LOGO_PATH = 'v1/img/shad/logo.svg'
PROJECT_DIR = Path(__file__).parents[1]

for template in TEMPLATES:
    if "Jinja2" in template["BACKEND"]:
        template["DIRS"] = [str(PROJECT_DIR / "jinja2")] + template["DIRS"]
        template["OPTIONS"]["constants"]["YANDEX_METRIKA_ID"] = YANDEX_METRIKA_ID
        update_constants = [
            ("ESTABLISHED", ESTABLISHED),
            ("FAVICON_PATH", FAVICON_PATH),
            ("LOGO_PATH", LOGO_PATH)
        ]
        for option, value in update_constants:
            template["OPTIONS"]["constants"][option] = value
    elif "DjangoTemplates" in template["BACKEND"]:
        template["DIRS"] = [str(PROJECT_DIR / "templates")] + template["DIRS"]


# Application form webhook authorization token. Send it over https only.
APPLICATION_FORM_SECRET_TOKEN = 'eb224e98-fffa-4e21-ab92-744f2e95e551-3f2a5499-89bf-4f8b-9c90-117b960f0fdf'
