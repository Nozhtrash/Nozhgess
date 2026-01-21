; ==============================================================================
;                    INNO SETUP - NOZHGESS v3.0 LEGENDARY
; ==============================================================================
; Script para crear instalador de Windows
;
; Requisitos:
;   1. Ejecutar primero: pyinstaller nozhgess.spec
;   2. Tener Inno Setup instalado
;   3. Compilar este script con Inno Setup Compiler
;
; Resultado:
;   Output/NozhgessSetup.exe
; ==============================================================================

#define MyAppName "Nozhgess"
#define MyAppVersion "3.0.0"
#define MyAppPublisher "Nozhtrash"
#define MyAppURL "https://github.com/Nozhtrash/nozhgess"
#define MyAppExeName "Nozhgess.exe"

[Setup]
; Identificador único de la aplicación
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Icono del instalador
; SetupIconFile=assets\icon.ico
; Información de licencia (opcional)
; LicenseFile=LICENSE
OutputDir=Output
OutputBaseFilename=NozhgessSetup
; Compresión
Compression=lzma2/ultra64
SolidCompression=yes
; Estilo moderno
WizardStyle=modern
; Requerir privilegios de admin
PrivilegesRequired=admin
; Arquitectura
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Archivos principales desde dist/Nozhgess
Source: "dist\Nozhgess\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Nozhgess\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Archivos adicionales
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "LEEME.txt"
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menú inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Escritorio
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Ejecutar después de instalar
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpiar archivos generados
Type: filesandordirs; Name: "{app}\Crash_Reports"
Type: filesandordirs; Name: "{app}\Z_Utilidades\Logs"
Type: files; Name: "{app}\*.log"

[Code]
// Código Pascal para verificaciones adicionales

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Verificar si ya está instalado
  if RegKeyExists(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1') then
  begin
    if MsgBox('Nozhgess ya está instalado. ¿Desea actualizar?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Crear directorios necesarios
    ForceDirectories(ExpandConstant('{app}\Crash_Reports'));
    ForceDirectories(ExpandConstant('{app}\Z_Utilidades\Logs'));
    ForceDirectories(ExpandConstant('{app}\Lista de Misiones\Reportes'));
  end;
end;
