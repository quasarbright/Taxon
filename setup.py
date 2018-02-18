import sys
import os
from cx_Freeze import setup, Executable
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os"],
    'include_files': [
        'MISTER-BRAINWASH.ico',
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll')
    ],
    "includes":['retrain','label_image','numpy.core._methods', 'numpy.lib.format']
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32"
executables = [
    Executable("app.py", base=base, icon='MISTER-BRAINWASH.ico'),
]

setup(name="Taxon",
      version="0.1",
      description="retrain inception with a GUI",
      options={"build_exe": build_exe_options},
      executables=executables
      )
