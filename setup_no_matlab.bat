@echo off
setlocal

REM Get the full path to the folder containing this batch script
set "script_dir=%~dp0"

REM Check if the virtual environment folder exists
if not exist "%script_dir%\venv" (
    python -m venv "%script_dir%\venv"
)

REM Activate the virtual environment and install requirements
call "%script_dir%\venv\Scripts\activate.bat"
call pip install -r "%script_dir%\requirements_no_matlab.txt"

REM Run setup.py
call python "%script_dir%\installer\setup_uninstall.py"

REM Run setup.py
call python "%script_dir%\setup.py"

REM Deactivate the virtual environment
call "%script_dir%\venv\Scripts\deactivate.bat"

endlocal
