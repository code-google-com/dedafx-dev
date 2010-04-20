@set PATH=C:\Program Files\NSIS;C:\Program Files (x86)\NSIS;%PATH%

:clean
rmdir /S /Q dist
rmdir /S /Q build

:pybuild
python setup.py py2exe

:addresources
copy VineyardInstaller.nsi dist\VineyardInstaller.nsi
copy gui\grapes.png dist\grapes.png
copy gui\splash.png dist\splash.png
copy res\header.bmp dist\header.bmp
copy res\license.txt dist\license.txt
copy res\startService.bat dist\startService.bat
copy res\stopService.bat dist\stopService.bat
copy c:\Python26\lib\site-packages\Pythonwin\mfc90.dll dist\mfc90.dll
xcopy /S /E doc\_build\html\* dist\doc\*

:make_documentation
rmdir /S /Q doc\_build
mkdir dist\doc
cd doc
call make.bat html
cd ..
xcopy /S /E plugins\*.pyc dist\plugins\*


:installbuild
makensis.exe ./dist/VineyardInstaller.nsi

:end
