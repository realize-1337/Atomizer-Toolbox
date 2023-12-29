if not exist venv (
    python -m venv venv
)

REM Activate the virtual environment and install requirements
call .\venv\Scripts\activate.bat 
call pip install -r requirements.txt

REM Run setup.py
call python setup.py

REM Deactivate the virtual environment
call .\venv\Scripts\deactivate.bat
