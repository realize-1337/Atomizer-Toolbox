if not exist venv (
    python -m venv venv
    echo Created a virtual environment
)

REM Activate the virtual environment and install requirements
call .\venv\Scripts\activate.bat 
call pip install -r requirements.txt

REM Display a message and wait for user input
set /p confirm=Press Enter to start building the software...

REM Run setup.py
call python setup.py

REM Deactivate the virtual environment
call .\venv\Scripts\deactivate.bat
