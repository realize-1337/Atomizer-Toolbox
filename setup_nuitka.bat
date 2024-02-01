@echo off

rem Set your project directory
set PROJECT_DIR=C:\Users\david\Documents\Dev\Atomizer-Toolbox

rem Set the path to the icon file
set ICON_PATH=assets\ATT_logo.ico
set PACKAGE_PATH = %PROJECT_DIR%\packages
set GUI_PATH = %PROJECT_DIR%\GUI
set M_PATH = %PROJECT_DIR%\matlab_scripts

rem Navigate to the project directory
cd %PROJECT_DIR%

rem Compile the project with Nuitka and set the icon
nuitka --standalone --include-data-dir=%PACKAGE_PATH%/=packages --include-data-dir=%GUI_PATH%/=GUI --include-data-dir=%M_PATH%/=matlab_scripts --follow-imports --windows-icon-from-ico=%ICON_PATH% --enable-plugin=pyside6 --include-qt-plugins=qml main.py

rem Pause to keep the terminal open for viewing any potential errors
pause
