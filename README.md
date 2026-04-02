# Django Bug Tracker (DjProj)

## Project overview

Django-based bug tracking app in `d:\aashu\DjangoPr\DjProj`.

- Includes:
  - bug report create/read/update
  - sprint management (lead developer + developers)
  - role-based users (Developer, Tester)
  - profile edit with custom permission `edit_user_profile_perm`
  - file-based upload (Excel `.xlsx`) for status update
  - file download of bug reports to Excel
  - API endpoints for bug stats
  - authentication (login/logout/register)
  - pagination for sprints

## Directory structure

- `bugenv/`: virtualenv root (Python binaries + packages)
- `bugenv/django_bugtracker/`: Django project
  - `django_bugtracker/settings.py`
  - `django_bugtracker/urls.py`
  - `django_bugtracker/wsgi.py`
- `bugenv/django_bugtracker/django_bugapp/`: app code
  - `models.py`, `views.py`, `forms.py`, `serializers.py`, `urls.py`, `admin.py`
- `bugenv/django_bugtracker/templates/`: templates
  - base, profile, login, register, bug pages, sprint pages
- `media/bug_screenshots/`: uploaded images
- `static`, `staticfiles`: static assets
- `db.sqlite3`: dev DB (ignored by `.gitignore`)

## Key features

- `Bug` model:
  - fields: `title`, `info`, `screenshot`, `platform`, `status`, `bug_id`, `sprint`, `time_spent_hours`
  - auto-generates `bug_id` as `BUG###`
- `Sprint` model:
  - fields: `name`, `lead_developer`, `developers`, `start_date`, `end_date`
- `UserProfile`:
  - phone validation
  - bio
- User management:
  - `CustomRegisterForm` with `role` select from `Group`
  - `login_required` everywhere needed
  - `permission_required('django_bugapp.edit_user_profile_perm')` for profile edit
- Business logic:
  - `fix_bug` view checks:
    - request user not creator
    - bug is unfixed
    - user in sprint developers
  - `bugreport` view:
    - Excel download via pandas/xlsxwriter
    - Excel upload for status updates / create missing
- API:
  - `DeveloperBugStatsView`: count created / completed
  - `BugDurationAPIView`: duration per bug
- Sprint UI:
  - list, detail, create, edit
  - aggregates avg and totals per developer/platform

## Python / Django versions and libs

- Django version in settings header: 5.2.1
- Python version from virtualenv path: 3.10
- likely installed:
  - Django
  - pandas
  - djangorestframework
  - django-widget-tweaks
  - django-seed
  - xlsxwriter (via pandas ExcelWriter)
  - maybe pillow (ImageField screenshot)
- requirements at `bugenv/requirements.txt` (sync to actual if not exact)

## Setup

1. open terminal at `d:\aashu\DjangoPr\DjProj`
2. Activate venv:
   - `.\bugenv\Scripts\Activate.ps1` (PowerShell)
3. install:
   - `pip install -r .\bugenv\requirements.txt`
4. make migrations + migrate:
   - `python .\bugenv\django_bugtracker\manage.py makemigrations`
   - `python .\bugenv\django_bugtracker\manage.py migrate`
5. create superuser:
   - `python .\bugenv\django_bugtracker\manage.py createsuperuser`
6. run dev server:
   - `python .\bugenv\django_bugtracker\manage.py runserver`
7. access:
   - `http://127.0.0.1:8000/django_bugapp/`

## .gitignore

Already present at project root:

- `__pycache__/`, `*.py[cod]`
- `venv/`, `env/`, `.venv/`, `bugenv/`
- `db.sqlite3`, `media/`, `staticfiles/`
- `.env`, `*.env`
- IDE files, OS files, logs

## Notes

- `settings.py` uses SQLite `BASE_DIR/db.sqlite3`; set up PostgreSQL for prod.
- `MEDIA_ROOT` points `BASE_DIR/media`.
- If migrating to production, switch `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Optionally remove `bugenv` from git if using local venv as ignored artifact.# Django Bug Tracker (DjProj)

## Project overview

Django-based bug tracking app in `d:\aashu\DjangoPr\DjProj`.

- Includes:
  - bug report create/read/update
  - sprint management (lead developer + developers)
  - role-based users (Developer, Tester)
  - profile edit with custom permission `edit_user_profile_perm`
  - file-based upload (Excel `.xlsx`) for status update
  - file download of bug reports to Excel
  - API endpoints for bug stats
  - authentication (login/logout/register)
  - pagination for sprints

## Directory structure

- `bugenv/`: virtualenv root (Python binaries + packages)
- `bugenv/django_bugtracker/`: Django project
  - `django_bugtracker/settings.py`
  - `django_bugtracker/urls.py`
  - `django_bugtracker/wsgi.py`
- `bugenv/django_bugtracker/django_bugapp/`: app code
  - `models.py`, `views.py`, `forms.py`, `serializers.py`, `urls.py`, `admin.py`
- `bugenv/django_bugtracker/templates/`: templates
  - base, profile, login, register, bug pages, sprint pages
- `media/bug_screenshots/`: uploaded images
- `static`, `staticfiles`: static assets
- `db.sqlite3`: dev DB (ignored by `.gitignore`)

## Key features

- `Bug` model:
  - fields: `title`, `info`, `screenshot`, `platform`, `status`, `bug_id`, `sprint`, `time_spent_hours`
  - auto-generates `bug_id` as `BUG###`
- `Sprint` model:
  - fields: `name`, `lead_developer`, `developers`, `start_date`, `end_date`
- `UserProfile`:
  - phone validation
  - bio
- User management:
  - `CustomRegisterForm` with `role` select from `Group`
  - `login_required` everywhere needed
  - `permission_required('django_bugapp.edit_user_profile_perm')` for profile edit
- Business logic:
  - `fix_bug` view checks:
    - request user not creator
    - bug is unfixed
    - user in sprint developers
  - `bugreport` view:
    - Excel download via pandas/xlsxwriter
    - Excel upload for status updates / create missing
- API:
  - `DeveloperBugStatsView`: count created / completed
  - `BugDurationAPIView`: duration per bug
- Sprint UI:
  - list, detail, create, edit
  - aggregates avg and totals per developer/platform

## Python / Django versions and libs

- Django version in settings header: 5.2.1
- Python version from virtualenv path: 3.10
- likely installed:
  - Django
  - pandas
  - djangorestframework
  - django-widget-tweaks
  - django-seed
  - xlsxwriter (via pandas ExcelWriter)
  - maybe pillow (ImageField screenshot)
- requirements at `bugenv/requirements.txt` (sync to actual if not exact)

## Setup

1. open terminal at `d:\aashu\DjangoPr\DjProj`
2. Activate venv:
   - `.\bugenv\Scripts\Activate.ps1` (PowerShell)
3. install:
   - `pip install -r .\bugenv\requirements.txt`
4. make migrations + migrate:
   - `python .\bugenv\django_bugtracker\manage.py makemigrations`
   - `python .\bugenv\django_bugtracker\manage.py migrate`
5. create superuser:
   - `python .\bugenv\django_bugtracker\manage.py createsuperuser`
6. run dev server:
   - `python .\bugenv\django_bugtracker\manage.py runserver`
7. access:
   - `http://127.0.0.1:8000/django_bugapp/`

## .gitignore

Already present at project root:

- `__pycache__/`, `*.py[cod]`
- `venv/`, `env/`, `.venv/`, `bugenv/`
- `db.sqlite3`, `media/`, `staticfiles/`
- `.env`, `*.env`
- IDE files, OS files, logs

## Notes

- `settings.py` uses SQLite `BASE_DIR/db.sqlite3`; set up PostgreSQL for prod.
- `MEDIA_ROOT` points `BASE_DIR/media`.
- If migrating to production, switch `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Optionally remove `bugenv` from git if using local venv as ignored artifact.
