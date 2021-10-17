from cx_Freeze import setup, Executable
import sys

# exclude unneeded packages. More could be added. Has to be changed for
# other programs.
build_exe_options = {"excludes": ["tkinter", "PyQt5", "PySide6","pandas","matplotlib", "PySide2.Qt5WebEngineCore",
                                  "scipy",
                                  "numpy"],
                     "optimize": 2}

# Information about the program and build command. Has to be adjusted for
# other programs
setup(
    name="DeClutter",                           # Name of the program
    version="1.12.1",                           # Version number
    description="DeClutter: file organizer",    # Description
    options = {"build_exe": build_exe_options}, # <-- the missing line
    executables=[Executable("DeClutter.py",     # Executable python file
                            base = ("Win32GUI" if sys.platform == "win32" 
                            else None))],
)