#define MyAppName "Speedtest Logger"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "kanzyy"
#define MyAppExeName "speedtest_logger.exe"

[Setup]
AppId={{2D3B47D0-2E10-4E12-91D8-0A67A9CCB42F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SpeedtestLogger
DefaultGroupName=Speedtest Logger
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=SpeedtestLoggerSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\speedtest_logger.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Speedtest Logger"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Speedtest Logger deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Speedtest Logger"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknuepfung erstellen"; GroupDescription: "Zusaetzliche Aufgaben:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Speedtest Logger jetzt starten"; Flags: nowait postinstall skipifsilent
