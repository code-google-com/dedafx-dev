; VineyardInstaller.nsi
;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

; The name of the installer
Name "Vineyard"

; The file to write
OutFile "VineyardInstaller.exe"

; The default installation directory
InstallDir $PROGRAMFILES\DedaFX\Vineyard

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\DedaFX\Vineyard" "InstallDir"

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
Section "Vineyard"

  ExecWait "$INSTDIR\VineyardService.exe stop"
  ExecWait "$INSTDIR\VineyardService.exe remove"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put files there
  File /r /x *.nsi *.*
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\DedaFX\Vineyard "InstallDir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vineyard" "DisplayName" "DedaFX Vineyard Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vineyard" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vineyard" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vineyard" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
  ; add startup to the users directory
  SetShellVarContext all
  CreateShortCut "$SMSTARTUP\VineyardManager.lnk" "$INSTDIR\FarmManager.exe" "" "$INSTDIR\FarmManager.exe" 0
  SetShellVarContext current

  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  SetShellVarContext all
  CreateDirectory "$SMPROGRAMS\DedaFX\Vineyard"
  CreateShortCut "$SMPROGRAMS\DedaFX\Vineyard\Vineyard Manager.lnk" "$INSTDIR\FarmManager.exe" "" "$INSTDIR\FarmManager.exe" 0
  ;CreateShortCut "$SMPROGRAMS\DedaFX\Vineyard\Install Service.lnk" "$INSTDIR\installService.bat" "" "$INSTDIR\installService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vineyard\Start Service.lnk" "$INSTDIR\startService.bat" "" "$INSTDIR\startService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vineyard\Stop Service.lnk" "$INSTDIR\stopService.bat" "" "$INSTDIR\stopService.bat" 0
  CreateShortCut "$SMPROGRAMS\DedaFX\Vineyard\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  SetShellVarContext current
  
SectionEnd

Section "Vineyard Service"

  ;ExecWait "NET USER vineyard_user Vineyard1_pa$$ /ADD /passwordchg:no /expires:never"
  ExecWait "$INSTDIR\VineyardService.exe stop"
  ExecWait "$INSTDIR\VineyardService.exe remove"
  ExecWait "$INSTDIR\VineyardService.exe --startup auto install" ;--username vineyard_user --password Vineyard1_pa$$ install"
  ExecWait "$INSTDIR\VineyardService.exe start"

SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\DedaFX\Vineyard"
  DeleteRegKey HKLM SOFTWARE\DedaFX\Vineyard

  ; Remove files and uninstaller
  Delete $INSTDIR\*.*

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\DedaFX\Vineyard\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\DedaFX\Vineyard"
  RMDir "$SMPROGRAMS\DedaFX"
  RMDir /r /REBOOTOK "$INSTDIR"
  RMDir "$INSTDIR\..\DedaFX"

SectionEnd
