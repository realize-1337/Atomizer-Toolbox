from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(sys.getrecursionlimit()*10)

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ['PyQt6.QtCore'],
                'excludes': [],
                'includes': ['PyQt6.QtCore']}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base, target_name = 'AtomizerToolBox')
]

setup(name='AtomizerToolBox',
      version = '1.6',
      description = '',
      options = {'build_exe': build_options},
      executables = executables)
