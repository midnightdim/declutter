; -- Example2.iss --
; Same as Example1.iss, but creates its icon in the Programs folder of the
; Start Menu instead of in a subfolder, and also creates a desktop icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=DeClutter
AppPublisher=Dmitry Beloglazov
AppVersion=1.12.1
WizardStyle=modern
DefaultDirName={autopf}\DeClutter
; Since no icons will be created in "{group}", we don't need the wizard
; to ask for a Start Menu folder name:
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\DeClutter.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputBaseFilename=DeClutter.latest
; OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "DeClutter.exe"; DestDir: "{app}"
Source: "python38.dll"; DestDir: "{app}"
Source: "python3.dll"; DestDir: "{app}"
Source: "DeClutter.ico"; DestDir: "{app}"
Source: "lib\*"; DestDir: "{app}\lib"; Flags: recursesubdirs
; Source: "icons\*"; DestDir: "{app}\icons"; Flags: recursesubdirs
; Source: "MyProg.chm"; DestDir: "{app}"
; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
;IconFilename: "{app}\DeClutter.ico"
Name: "{autostartup}\DeClutter"; Filename: "{app}\DeClutter.exe"; Tasks:StartMenuEntry;
Name: "{autoprograms}\DeClutter"; Filename: "{app}\DeClutter.exe"; IconFilename: "{app}\DeClutter.ico"
Name: "{autodesktop}\DeClutter"; Filename: "{app}\DeClutter.exe"; IconFilename: "{app}\DeClutter.ico"; Tasks: desktopicon
Name: "{group}\Uninstall DeClutter"; Filename: "{uninstallexe}"; IconFilename: "{app}\DeClutter.ico"

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; Flags: unchecked 
Name: StartMenuEntry; Description: "Start DeClutter service when Windows starts"
;Name: StartAfterInstall; Description: Run application after install

[Run]
Filename: {app}\{cm:AppName}.exe; Description: {cm:LaunchProgram,{cm:AppName}}; Flags: nowait postinstall skipifsilent

[CustomMessages]
AppName=DeClutter
LaunchProgram=Start DeClutter after finishing installation