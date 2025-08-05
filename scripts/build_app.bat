REM Run this from project root
python setup.py build

copy scripts\win_build_files_to_delete.txt build\exe.win-amd64-3.13\lib\PySide6\files_to_delete.txt

REM copy DeClutter.ico build\exe.win-amd64-3.13\DeClutter.ico
REM copy DeClutter.iss build\exe.win-amd64-3.13\DeClutter.iss

REM Navigate and delete
cd build\exe.win-amd64-3.13\lib\PySide6
for /f %%i in (files_to_delete.txt) do del /q %%i 2>nul
del files_to_delete.txt
rmdir /s /q translations
rmdir /s /q qml

REM Run Inno Setup if using DeClutter.iss
REM "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" DeClutter.iss
