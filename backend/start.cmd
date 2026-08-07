@echo off
:: Startup wrapper for the Flask backend, auto-detecting the virtualenv directory.

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

:: Normalize the path (resolve ..)
for %%i in ("%PROJECT_ROOT%") do set PROJECT_ROOT=%%~fi

set VENV_PATH=

if exist "%PROJECT_ROOT%\AAVAI\Scripts\activate.bat" (
    set VENV_PATH=%PROJECT_ROOT%\AAVAI
) else if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    set VENV_PATH=%PROJECT_ROOT%\venv
) else if exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    set VENV_PATH=%PROJECT_ROOT%\.venv
) else if exist "%SCRIPT_DIR%AAVAI\Scripts\activate.bat" (
    set VENV_PATH=%SCRIPT_DIR%AAVAI
)

if defined VENV_PATH (
    echo Activating virtual environment at %VENV_PATH%...
    call "%VENV_PATH%\Scripts\activate.bat"
) else (
    echo No virtual environment found, running with system python...
)

set PYTHONPATH=%PROJECT_ROOT%
cd /d "%PROJECT_ROOT%" && python -m backend.app
