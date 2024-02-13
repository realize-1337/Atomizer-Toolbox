import subprocess
import os
import sys
sys.setrecursionlimit(sys.getrecursionlimit()*5)

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

FILE = f'{os.path.join(dir_path, "setup_uninstall.py")}'
PROJECTNAME = 'uninstall'
AUTHOR = 'David Maerker'

# Führe PyInstaller aus
# print("Führe PyInstaller aus...")
print('Compiling uninstaller')
makeSpec = [
    "pyi-makespec",
    "--onefile",   # Eine einzelne ausführbare Datei erstellen
    # Hier können Sie weitere PyInstaller-Optionen hinzufügen
    "--noconsole", 
    # "--windowed",
    "--name", f"{PROJECTNAME}",
    "--icon", f"{os.path.join(os.path.dirname(dir_path), 'assets/ATT_LOGO.ico')}",
    # "--exclude-module", "module_to_exclude",
    # "--hidden-import", "matlab",
    # "--upx-dir", "path/to/upx",
    # "--additional-hooks-dir", "path/to/hooks",
    "--specpath", f"{os.path.join(dir_path, 'build/spec')}",
    # "--additional-hook-dir=hooks",
    # "--paths", "<path to the "matlab" folder>"
    # "--workpath", "work_directory",
    "--log-level", "WARN",
    FILE
]
try:
    subprocess.run(makeSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)

runSpec = [
    'pyinstaller',
    '--distpath', f'{dir_path}',
    "--workpath", "build/work",
    f'{os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec")}'
]

try: 
    subprocess.run(runSpec, check=True)
except subprocess.CalledProcessError as e:
    print('#'*100)
    print(' ERROR '*10)
    print('#'*100)
    print('Trying to automatically adjust spec file')
    with open(os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec"), "r") as specFile:
        lines = specFile.readlines()

    with open(os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec"), "w") as specFile:
        specFile.write(lines[0])
        specFile.write('import sys; \n')
        specFile.write('sys.setrecursionlimit(sys.getrecursionlimit()*10);\n')
        specFile.writelines(lines[1:])
    subprocess.run(runSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)
