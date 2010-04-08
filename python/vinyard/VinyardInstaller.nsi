; VinyardInstaller.nsi
;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

; The name of the installer
Name "Vinyard"

; The file to write
OutFile "VinyardInstaller.exe"

; The default installation directory
InstallDir $PROGRAMFILES\DedaFX\Vinyard

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\DedaFX\Vinyard" "InstallDir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

;Page components
;Page directory
;Page instfiles

;UninstPage uninstConfirm
;UninstPage instfiles

;--------------------------------

;--------------------------------
;Interface Settings

  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "header.bmp" ; optional
  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "license.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"
  
  

; The stuff to install
Section "Vinyard"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put files there
  File /r /x *.nsi *.*
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\DedaFX\Vinyard "InstallDir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vinyard" "DisplayName" "DedaFX Vinyard Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vinyard" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vinyard" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vinyard" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\DedaFX\Vinyard"
  CreateShortCut "$SMPROGRAMS\DedaFX\Vinyard\Vinyard Manager.lnk" "$INSTDIR\FarmManager.exe" "" "$INSTDIR\FarmManager.exe" 0
  ;CreateShortCut "$SMPROGRAMS\DedaFX\Vinyard\Install Service.lnk" "$INSTDIR\installService.bat" "" "$INSTDIR\installService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vinyard\Start Service.lnk" "$INSTDIR\startService.bat" "" "$INSTDIR\startService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vinyard\Stop Service.lnk" "$INSTDIR\stopService.bat" "" "$INSTDIR\stopService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vinyard\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  
  
SectionEnd

Section "Vinyard Service"

  ExecWait "$INSTDIR\VinyardService.exe remove"
  ExecWait "$INSTDIR\VinyardService.exe --startup auto install"
  ExecWait "$INSTDIR\VinyardService.exe start"

SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vinyard"
  DeleteRegKey HKLM SOFTWARE\DedaFX\Vinyard

  ; Remove files and uninstaller
  Delete $INSTDIR\*.*

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\DedaFX\Vinyard\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\DedaFX\Vinyard"
  RMDir "$SMPROGRAMS\DedaFX"
  RMDir /r /REBOOTOK "$INSTDIR"
  RMDir "$INSTDIR\..\DedaFX"

SectionEnd
