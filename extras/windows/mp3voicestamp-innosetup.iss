
; MP3 Voice Stamp
;
; Athletes' companion: adds synthetized voice overlay with various
; info and on-going timer to your audio files
;
; Copyright ©2018 Marcin Orlowski <mail [@] MarcinOrlowski.com>
;
; https://github.com/MarcinOrlowski/Mp3VoiceStamp

;
; Expected source tree layout:
; --------------------------------
; [root]
;    icon.ico          
;    installer-small-image.bmp
;    installer-big-image.bmp
;    post-install.txt
;    pre-install.txt
;    license.txt
;
;    tools\
;      sox\
;        sox.exe
;        *.dll
;      espeak\
;        espeak-data\
;        espeak.exe
;      bin\
;        ffmpeg.exe
;        normalize.exe
;    mp3voicestamp_app\
;      dist\
;        mp3voicestamp\
;          (output from pyinstaller)


#define MyAppName "Mp3VoiceStamp"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Marcin Orlowski"
#define MyAppURL "https://github.com/MarcinOrlowski/Mp3VoiceStamp"
#define MyAppExeName "mp3voicestamp.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{0B9D3C70-4B56-45E4-BF4B-E88426A0F203}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Mp3VoiceStamp-v{#MyAppVersion}-Setup
SetupIconFile=innosetup\icon.ico
Compression=lzma
SolidCompression=yes
InfoBeforeFile=innosetup\pre-install.txt
InfoAfterFile=innosetup\post-install.txt

LicenseFile=innosetup\license.txt

; http://www.jrsoftware.org/ishelp/index.php?topic=setup_wizardimagefile
; 55x55 px, 8-bit (no colorspace)
WizardSmallImageFile=innosetup\installer-small-image.bmp

; 164×314 px, 8-bit (no colorspace)
; NOTE: when saving from GIMP, enable "Do not write color space info" in 
; "Compatibility" section of BMP exporter or it won't "work" in InnoSetup!
WizardImageFile=innosetup\installer-big-image.bmp

; Tell Windows Explorer to reload the environment
ChangesEnvironment=yes

[Registry]
; set PATH
Root: HKCU; Subkey: "Environment"; ValueType:string; ValueName:"PATH"; ValueData:"{olddata};{app}"; Flags: preservestringtype

; path to espeak-data otherwise voice synthesis will not work when path is with space 
; as for some reasons --path is not really doing the trick on windows
Root: HKCU; Subkey: "Environment"; ValueType:string; ValueName:"ESPEAK_DATA_PATH"; ValueData:"{app}"; Flags: preservestringtype

;[Run]
;Filename: "{tmp}\sox-14.4.2-win32.exe"; Flags: waituntilterminated; Components: sox
;Filename: "{tmp}\setup_espeak-1.48.04.exe"; Flags: waituntilterminated; Components: espeak

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

;[Types]
;Name: "full"; Description: "Full installation"
;Name: "custom"; Description: "Custom installation"; Flags: iscustom

;[Components]
;Name: "program"; Description: "Program files"; Types: full custom; Flags: fixed
;Name: "sox"; Description: "Sox sound processing tool"; Types: full custom
;Name: "espeak"; Description: "eSpeak voice synthetizer"; Types: full custom

[Files]
;Source: "mp3voicestamp_app\dist\mp3voicestamp\mp3voicestamp.exe"; DestDir: "{app}"; Flags: ignoreversion; Components: program
Source: "mp3voicestamp_app\dist\mp3voicestamp\mp3voicestamp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "mp3voicestamp_app\dist\mp3voicestamp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs 
Source: "tools\bin\*"; DestDir: "{app}"; Flags: ignoreversion

; espeak 1.48.04
;Source: "tools\installers\setup_espeak-1.48.04.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall ignoreversion uninsremovereadonly; Components: espeak
;Source: "tools\espeak\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: espeak 
Source: "tools\espeak\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; sox 14.4.2
;Source: "tools\sox\*"; DestDir: "{app}"; Flags: ignoreversion; Components: sox
Source: "tools\sox\*"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

