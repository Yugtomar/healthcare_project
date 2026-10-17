@echo off
setlocal
pushd "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 goto :error
)

echo Installing packages...
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Creating database tables...
"venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 goto :error

echo.
echo Setup finished. Starting server at http://127.0.0.1:8000/
"venv\Scripts\python.exe" manage.py runserver
set "exit_code=%errorlevel%"
popd
exit /b %exit_code%

:error
set "exit_code=%errorlevel%"
popd
exit /b %exit_code%
