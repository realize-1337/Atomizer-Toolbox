import subprocess
import os
import sys
import packages.editMatlabEngine as edit
sys.setrecursionlimit(sys.getrecursionlimit()*5)

FILE = f'{os.path.abspath("./main.py")}'
PROJECTNAME = 'AtomizerToolbox'
VERSION = '1.66.1'
AUTHOR = 'David Maerker'

# Aktualisiere die Abhängigkeiten mit 'pip freeze'
# print("Aktualisiere Abhängigkeiten mit 'pip freeze'...")
# with open("requirements.txt", "w") as requirements_file:
#     subprocess.check_call(["pip", "freeze"], stdout=requirements_file)

# Edit matlab engine arch file, which otherwise would cause issues
try:
    edit.edit()
except:
    raise ModuleNotFoundError()

# Führe PyInstaller aus
print("Führe PyInstaller aus...")
makeSpec = [
    "pyi-makespec",
    "--onefile",   # Eine einzelne ausführbare Datei erstellen
    # Hier können Sie weitere PyInstaller-Optionen hinzufügen
    "--noconsole", 
    # "--windowed",
    "--name", f"{PROJECTNAME}_V{VERSION}",
    "--icon", f"{os.path.relpath('../../assets/ATT_LOGO.ico')}",
    "--add-data", f"{os.path.relpath('../../GUI')}\\*.py;GUI",
    "--add-data", f"../../packages/*.py;packages",
    "--add-data", f"../../matlab_scripts/*.m;matlab_scripts",
    "--add-data", f"{os.path.relpath('../../assets')};assets",
    # "--exclude-module", "module_to_exclude",
    "--hidden-import", "sympy",
    "--hidden-import", "skimage",
    "--hidden-import", "pyi_splash",
    # "--hidden-import", "matlab",
    # "--upx-dir", "path/to/upx",
    # "--additional-hooks-dir", "path/to/hooks",
    "--specpath", "build/spec",
    # "--additional-hook-dir=hooks",
    # "--paths", "<path to the "matlab" folder>"
    # "--workpath", "work_directory",
    "--log-level", "WARN",
    '--splash', f"{os.path.relpath('../../assets/splash_screen.png')}",
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