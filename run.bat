@echo off
pushd "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup.bat first.
    popd
    exit /b 1
)
"venv\Scripts\python.exe" manage.py runserver
set "exit_code=%errorlevel%"
popd
exit /b %exit_code%
