from cx_Freeze import setup, Executable
import sys
import os

build_exe_options = {
    "excludes": [
        "tkinter", "pandas", "matplotlib",
        "scipy", "numpy"
    ],
    "packages": ["os", "sys", "collections", "PySide6", "declutter", "requests", "certifi", "charset_normalizer"],
    "include_files": [
        os.path.join("assets", "DeClutter.ico"),
        os.path.join("scripts", "DeClutter.iss")
    ],
    "optimize": 2,
    "include_msvcr": True
}

setup(
    name="DeClutter",
    version="1.31.1",
    description="DeClutter: file organizer",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            os.path.join("src", "DeClutter.py"),
            base="Win32GUI" if sys.platform == "win32" else None,
            icon=os.path.join("assets", "DeClutter.ico")
        )
    ],
)
