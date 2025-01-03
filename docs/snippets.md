#### Snippets

```
# Minimal html to render debug toolbar in django views 
return HttpResponse("<html><body>body tag should be returned</body></html>", content_type='text/html; charset=utf-8')

# Recreate DB
psql -h localhost postgres -c "DROP DATABASE cscdb;"; psql -h localhost postgres -c "CREATE DATABASE cscdb WITH encoding 'UTF-8' LC_COLLATE='C' TEMPLATE=template0;"; psql -h localhost postgres -c "GRANT ALL privileges ON DATABASE cscdb TO csc;"
psql -h localhost cscdb csc < 
psql -h localhost cscdb csc -c "update django_site set domain='csc.test' where id = 1; update django_site set domain = 'club.ru' where id = 2; update django_site set domain = 'lk.shad.test' where id = 3;"
./manage.py update_site_configuration --settings=site_ru.settings.local
./manage.py changepassword admin
# TODO: Write ansible command to automate routine

# Disable annoying debug messages in ipython
import logging
logging.getLogger('parso.python.diff').disabled = True

# Enable sql console logger
import logging
from core.logging import SQLFormatter
sql_console_handler = logging.StreamHandler()
sql_console_handler.setLevel(logging.DEBUG)
formatter = SQLFormatter('[%(duration).3f] %(statement)s')
sql_console_handler.setFormatter(formatter)
logger = logging.getLogger('django.db.backends')
logger.addHandler(sql_console_handler)

# ...debug queries...

logger.removeHandler(sql_console_handler)
# Run rqworker on Mac OS High Sierra
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES ./manage.py rqworker default high
# Hotfix for ipython `DEBUG parser diff`
import logging; logging.getLogger('parso.python.diff').setLevel('INFO')
# Enable DEBUG in shell
logging.basicConfig(level=logging.DEBUG)  
```
