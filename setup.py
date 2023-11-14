import subprocess
import os
import sys
sys.setrecursionlimit(sys.getrecursionlimit()*5)

FILE = f'{os.path.abspath("./main.py")}'
PROJECTNAME = 'AtomizerToolbox'
VERSION = '1.3'
AUTHOR = 'David Maerker'

# Aktualisiere die Abhängigkeiten mit 'pip freeze'
print("Aktualisiere Abhängigkeiten mit 'pip freeze'...")
with open("requirements.txt", "w") as requirements_file:
    subprocess.check_call(["pip", "freeze"], stdout=requirements_file)

# Führe PyInstaller aus
print("Führe PyInstaller aus...")
makeSpec = [
    "pyi-makespec",
    "--onefile",   # Eine einzelne ausführbare Datei erstellen
    # Hier können Sie weitere PyInstaller-Optionen hinzufügen
    "--noconsole", 
    # "--windowed",
    "--name", f"{PROJECTNAME}_V{VERSION}",
    # "--icon", "your_icon.ico",
    "--add-data", f"{os.path.relpath('../../GUI')}\\*.py;GUI",
    "--add-data", f"../../packages/*.py;packages",
    # "--exclude-module", "module_to_exclude",
    "--hidden-import", "sympy",
    # "--upx-dir", "path/to/upx",
    # "--additional-hooks-dir", "path/to/hooks",
    "--specpath", "build/spec",
    # "--workpath", "work_directory",
    # "--log-level", "INFO",
    FILE
]
try:
    subprocess.run(makeSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)

runSpec = [
    'pyinstaller',
    '--distpath', '',
    "--workpath", "build/work",
    f'{os.path.abspath(f"build/spec/{PROJECTNAME}_V{VERSION}.spec")}'
]

try: 
    subprocess.run(runSpec, check=True)
except subprocess.CalledProcessError as e:
    print('#'*100)
    print(' ERROR '*10)
    print('#'*100)
    print('Trying to automatically adjust spec file')
    with open(os.path.abspath(f"build/spec/{PROJECTNAME}_V{VERSION}.spec"), "r") as specFile:
        lines = specFile.readlines()

    with open(os.path.abspath(f"build/spec/{PROJECTNAME}_V{VERSION}.spec"), "w") as specFile:
        specFile.write(lines[0])
        specFile.write('import sys; \n')
        specFile.write('sys.setrecursionlimit(sys.getrecursionlimit()*10);\n')
        specFile.writelines(lines[1:])
    subprocess.run(runSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)