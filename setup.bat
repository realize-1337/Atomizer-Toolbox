@echo off

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment and install requirements
venv\Scripts\activate.bat && pip install -r requirements.txt

REM Run setup.py
python setup.py

REM Deactivate the virtual environment
venv\Scripts\deactivate.bat
