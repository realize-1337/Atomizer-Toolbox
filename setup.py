import subprocess
import os
import sys
import packages.editMatlabEngine as edit
import json
import shutil
sys.setrecursionlimit(sys.getrecursionlimit()*5)

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

FILE = f'{os.path.join(dir_path, "main.py")}'
PROJECTNAME = 'AtomizerToolbox'
VERSION = '1.68.3'
AUTHOR = 'David Maerker'


settings = {'currentVersion': VERSION}
versionInfo = os.path.join(dir_path, 'assets/versioninfo.json')
with open(versionInfo, 'w') as file:
    json.dump(settings, file, indent=4)

# Edit matlab engine arch file, which otherwise would cause issues
try:
    edit.edit()
except:
    raise ModuleNotFoundError()

# Führe PyInstaller aus
print("Running PyInstaller ...")
makeSpec = [
    "pyi-makespec",
    "--onedir",   # Eine einzelne ausführbare Datei erstellen
    # Hier können Sie weitere PyInstaller-Optionen hinzufügen
    "--noconsole", 
    # "--windowed",
    "--name", f"{PROJECTNAME}",
    "--icon", f"{os.path.join(dir_path, 'assets/ATT_LOGO.ico')}",
    "--add-data", f"{os.path.join(dir_path, 'GUI')}\\*.py;GUI",
    "--add-data", f"{os.path.join(dir_path, 'packages')}/*.py;packages",
    "--add-data", f"{os.path.join(dir_path, 'matlab_scripts')}/*.m;matlab_scripts",
    "--add-data", f"{os.path.join(dir_path, 'assets')};assets",
    "--version-file", f"{os.path.join(dir_path, 'version_sign/versionfile_installer.txt')}",
    # "--exclude-module", "module_to_exclude",
    "--hidden-import", "sympy",
    "--hidden-import", "skimage",
    "--hidden-import", "pyi_splash",
    # "--hidden-import", "matlab",
    # "--upx-dir", "path/to/upx",
    # "--additional-hooks-dir", "path/to/hooks",
    "--specpath", f"{os.path.join(dir_path, 'build/spec')}",
    # "--additional-hook-dir=hooks",
    # "--paths", "<path to the "matlab" folder>"
    # "--workpath", "work_directory",
    "--log-level", "WARN",
    '--splash', f"{os.path.join(dir_path, 'assets/splash_screen.png')}",
    FILE
]
try:
    subprocess.run(makeSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)

runSpec = [
    'pyinstaller',
    '--distpath', f'{dir_path}',
    "--workpath", f"{dir_path}/build/work",
    f'{os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec")}'
]


try: 
    subprocess.run(runSpec, check=True)
except subprocess.CalledProcessError as e:
    print('Trying to automatically adjust spec file')
    with open(os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec"), "r") as specFile:
        lines = specFile.readlines()

    with open(os.path.join(dir_path, f"build/spec/{PROJECTNAME}.spec"), "w") as specFile:
        specFile.write(lines[0])
        specFile.write('import sys; \n')
        specFile.write('sys.setrecursionlimit(sys.getrecursionlimit()*10);\n')
        specFile.writelines(lines[1:])
    print('Edit done! Working on compile. Please wait ...')
    subprocess.run(runSpec)
except subprocess.CalledProcessError as e:
    raise SystemExit(e)

try: 
    shutil.copy(os.path.join(dir_path, 'installer/uninstall.exe'), os.path.join(dir_path, 'AtomizerToolbox/uninstall.exe'))
except: 
    pass

print('***Compile Done***\n'*10)

