Production stack: nginx, uwsgi, python3.x, Django 2.2.x, postgresql 11, redis (for queue)


```bash
cp docker-compose.override.yml.example docker-compose.override.yml
cp ./lms/settings/.env.example ./lms/settings/.env
docker exec -e RECAPTCHA_PRIVATE_KEY= -e RECAPTCHA_PUBLIC_KEY= -it lms-backend-1 ./manage.py migrate --settings=site_ru.settings.production

docker exec -e RECAPTCHA_PRIVATE_KEY= -e RECAPTCHA_PUBLIC_KEY= -it lms-backend-1 ./manage.py createsuperuser --settings=site_ru.settings.production
docker exec -e RECAPTCHA_PRIVATE_KEY= -e RECAPTCHA_PUBLIC_KEY= -it lms-backend-1 ./manage.py shell --settings=site_ru.settings.production
```


```python
from users.models import StudentProfile, User, StudentTypes
from django.contrib.auth.hashers import make_password
from core.models import Branch
from courses.models import Semester, Course, MetaCourse
from learning.models import EnrollmentPeriod
from learning.settings import InvitationEnrollmentTypes
from django.conf import settings
import datetime

main_branch = Branch.objects.create(code="main", name_ru="Главное отделение", name_en="Main Branch", established=2024, site_id=settings.SITE_ID, time_zone="Europe/Moscow")
current_term = Semester.get_current()
EnrollmentPeriod.objects.create(site_id=settings.SITE_ID, semester=current_term)
admin = User.objects.create(username="admin", email="admin@localhost.ru", is_superuser=True, is_staff=True, time_zone='Europe/Moscow', password=make_password("123123"))
StudentProfile.objects.create(site_id=settings.SITE_ID, user=admin, type=StudentTypes.VOLUNTEER, branch=main_branch, year_of_admission=2024)

meta_course = MetaCourse.objects.create(slug="first-course-slug", name_ru="Первый Курс", name_en="First Course")
# Первое прочтение курса
course = Course.objects.create(meta_course=meta_course, semester=current_term, main_branch=main_branch, enrollment_type=InvitationEnrollmentTypes.LECTIONS_ONLY, completed_at=datetime.datetime.now(datetime.timezone.utc), is_draft=False)
```
