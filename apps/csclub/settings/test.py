from .base import *

# Test settings

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = str(PROJECT_DIR)
TEST_DISCOVER_ROOT = str(PROJECT_DIR)
TEST_DISCOVER_PATTERN = "test_*"

# django-coverage settings

COVERAGE_REPORT_HTML_OUTPUT_DIR = str(PROJECT_DIR / "coverage")
COVERAGE_USE_STDOUT = True
COVERAGE_MODULE_EXCLUDES = ['tests$', 'settings$', 'urls$', 'locale$',
                            'common.views.test', '__init__', 'django',
                            'migrations', '^sorl', '__pycache__']
COVERAGE_PATH_EXCLUDES = [r'.svn', r'fixtures', r'node_modules']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "travis_ci_test",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": ""
    }
}


ALLOWED_HOSTS = [".compscicenter.ru", ".compsciclub.ru"]
# This makes tests almost 2x faster; we don't need strong security and DEBUG
# during tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
DEBUG = False
for template in TEMPLATES:
    template['OPTIONS']['debug'] = DEBUG

MEDIA_ROOT = '/tmp/django_test_media/'

MIGRATION_MODULES = {}

LANGUAGE_CODE = 'en'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'