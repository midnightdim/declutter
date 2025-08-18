#define MyAppName "DeClutter"
#define RawVersion GetVersionNumbersString("DeClutter.exe")

; Strip trailing `.0` if it exists
#if Copy(RawVersion, Len(RawVersion)-1, 2) == ".0"
  #define MyAppVersion Copy(RawVersion, 1, Len(RawVersion)-2)
#else
  #define MyAppVersion RawVersion
#endif

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Dmitry Beloglazov
WizardStyle=modern
DefaultDirName={autopf}\{#MyAppName}
; Since no icons will be created in "{group}", we don't need the wizard
; to ask for a Start Menu folder name:
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppName}.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputBaseFilename={#MyAppName}-{#MyAppVersion}-Windows-x64
; OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "{#MyAppName}.exe"; DestDir: "{app}"
Source: "python313.dll"; DestDir: "{app}"
Source: "python3.dll"; DestDir: "{app}"
Source: "{#MyAppName}.ico"; DestDir: "{app}"
Source: "lib\*"; DestDir: "{app}\lib"; Flags: recursesubdirs
; Source: "icons\*"; DestDir: "{app}\icons"; Flags: recursesubdirs
; Source: "MyProg.chm"; DestDir: "{app}"
; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
;IconFilename: "{app}\{#MyAppName}.ico"
Name: "{autostartup}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; Tasks:StartMenuEntry;
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; IconFilename: "{app}\{#MyAppName}.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; IconFilename: "{app}\{#MyAppName}.ico"; Tasks: desktopicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\{#MyAppName}.ico"

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; Flags: unchecked 
Name: StartMenuEntry; Description: "Start {#MyAppName} when Windows starts"
;Name: StartAfterInstall; Description: Run application after install

[Run]
Filename: {app}\{cm:AppName}.exe; Description: {cm:LaunchProgram,{cm:AppName}}; Flags: nowait postinstall skipifsilent

[CustomMessages]
AppName={#MyAppName}
LaunchProgram=Start {#MyAppName} after finishing installation
