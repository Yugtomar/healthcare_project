# Healthcare Backend

A small backend for a healthcare app built with Django, Django REST Framework and SQLite. Users can register, log in (JWT), manage patients and doctors, and assign doctors to patients.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

Alternatively, run `setup.bat` once to install dependencies, create the database, and start the server; use `run.bat` for later starts.

The default database is `db.sqlite3` in the project directory. Create an account at `http://127.0.0.1:8000/register/` to open the CarePoint workspace.

## Web app

The interface includes a dashboard, private patient records, a shared doctor directory, and patient-doctor assignments. The web app and API use the same database.

## API endpoints

- `POST /api/auth/register/` — Register an account.
- `POST /api/auth/login/` — Log in and receive JWT tokens.
- `/api/patients/` — Create and manage your patient records.
- `/api/doctors/` — Browse and manage the shared doctor directory.
- `/api/mappings/` — Assign doctors to patients and manage care teams.
- `/admin/` — Django administration.

API endpoints other than registration and login require a JWT `Authorization: Bearer <access-token>` header.

## Notes

- Email is used as the username.
- Patients are private: each user only sees records they created.
- Doctors are visible to logged-in users; only a doctor’s creator can edit or delete that profile.
- Secrets live in `.env` (git-ignored). Start from `.env.example` for local configuration.
