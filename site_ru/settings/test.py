from .base import *

DEBUG = False
MODELTRANSLATION_DEBUG = False
THUMBNAIL_DEBUG = False
for template in TEMPLATES:
    template['OPTIONS']['debug'] = DEBUG
    if 'auto_reload' in template['OPTIONS']:
        template['OPTIONS']['auto_reload'] = DEBUG



TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = str(SHARED_APPS_DIR)
TEST_DISCOVER_ROOT = str(SHARED_APPS_DIR)
TEST_DISCOVER_PATTERN = "test_*"

# django-coverage settings
COVERAGE_REPORT_HTML_OUTPUT_DIR = str(SHARED_APPS_DIR / "coverage")
COVERAGE_USE_STDOUT = True
COVERAGE_MODULE_EXCLUDES = ['tests$', 'settings$', 'urls$', 'locale$',
                            'common.views.test', '__init__', 'django',
                            'migrations', '^sorl', '__pycache__']
COVERAGE_PATH_EXCLUDES = [r'.svn', r'fixtures', r'node_modules']

# FIXME: don't use this settings, try to remove them from tests
TEST_DOMAIN = 'lk.yandexdataschool.ru'
TEST_DOMAIN_ID = 1
ANOTHER_DOMAIN = 'www.yandexdataschool.ru'
ANOTHER_DOMAIN_ID = 2
SITE_ID = TEST_DOMAIN_ID
ALLOWED_HOSTS = [f".{TEST_DOMAIN}", f".{ANOTHER_DOMAIN}"]

# This makes tests almost 2x faster; we don't need strong security and DEBUG
# during tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
PRIVATE_FILE_STORAGE = DEFAULT_FILE_STORAGE
MEDIA_ROOT = '/tmp/django_test_media/'
MEDIA_URL = "/media/"
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_SEND_COOLDOWN = 0

MIGRATION_MODULES = {}

LANGUAGE_CODE = 'en'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

for queue_config in RQ_QUEUES.values():
    queue_config['ASYNC'] = False

# Disable gerrit ldap password hash sync
LDAP_SYNC_PASSWORD = False

for bundle_conf in WEBPACK_LOADER.values():
    bundle_conf['LOADER_CLASS'] = 'core.webpack_loader.TestingWebpackLoader'

