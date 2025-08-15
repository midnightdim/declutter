@echo off
REM This script builds the DeClutter application for Windows using PyInstaller.

cd ..
python setup.py build

copy scripts\win_build_files_to_delete.txt build\exe.win-amd64-3.13\lib\PySide6\files_to_delete.txt

copy DeClutter.ico build\exe.win-amd64-3.13\DeClutter.ico
copy scripts\DeClutter.iss build\exe.win-amd64-3.13\DeClutter.iss

REM Navigate and delete
cd build\exe.win-amd64-3.13\lib\PySide6
for /f %%i in (files_to_delete.txt) do del /q %%i 2>nul
del files_to_delete.txt
rmdir /s /q translations
rmdir /s /q qml
cd ../..

REM Run Inno Setup to create the installer
echo "The application has been built."
echo "You can now create an installer using Inno Setup."
set /p build_installer="Do you want to build the installer now? (y/n) "
if /i "%build_installer%"=="y" (
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "DeClutter.iss"
    ) else (
        echo "Inno Setup is not installed in the default location."
        echo "Please install Inno Setup or update the path in the script."
        pause
    )
)
