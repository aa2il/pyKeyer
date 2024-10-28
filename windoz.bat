@echo off
echo %DATE% %TIME%
goto BUILD
echo.
echo Notes about how to run pyKeyer on Windoze 10
echo.
echo Should already installed most of what we need:
echo.
        pip install -r requirements.txt
echo.
echo Run the script under python (an exmaple):
echo The automatic determination of the keying device does not work (yet)
echo under windows so we have to specify the keying device, e.g.
echo.
         pyKeyer.py -prac -cwt -adjust -wpm 30 -keyer WINKEY
echo.
echo. Paddling practice also works but the keyer is currently hardwired to WINKEY
echo.
         paddling.py
echo.
echo There are two modules that are used, pyudev and termios, that
echo appear to be linux-only.  They have been disabled but it remains to be
echo if some substitute is needed...
echo.
:BUILD
echo.
echo To compile - this takes a while and spews a bunch of errors but works anyways:
echo.
         pyinstaller --onefile pyKeyer.py
         copy ..\data\cty.plist dist
	 copy Book.txt dist
	 copy Panagrams.txt dist
	 copy Stumble.txt dist
	 copy QSO_Template.txt dist
	 copy keyer_splash.png dist
	 copy ..\..\AA2IL\master.csv dist
         copy Release_Notes.txt dist
         copy practice.bat dist
         del dist\Output\pyKeyer_setup.exe
echo.
echo On linux:
echo "    cp ../data/cty.plist Book.txt Panagrams.txt Stumble.txt QSO_Template.txt keyer_splash.png ~/AA2IL/master.csv dist"
echo.
echo Run compiled version (example):
         dist\pyKeyer.exe -prac -sidetone -cwt -adjust -wpm 30
echo.
echo The good news:
echo     - CWT practice works great!
echo     - It can find and use the nano_io!
echo     - It does find the rig and nanoIO on windows
echo.
echo Known issue(s):
echo     0. Compiled version seems just fine under linux.
echo        May need pavucontrol to direct pulse audio output.   
echo     1. Rig control and keying under windoz doesn't work (yet)
echo.
echo Run Inno Setup Compiler and follow the prompts to create an installer
echo This installer works on Windoz 10 and Bottles!
echo Be sure to include the following files:
echo      keyer_splash.png   - need to rename this to be program specific
echo      Book.txt, Panagrams.txt, Stumble.txt and QSO_Template.txt
echo      state.json
echo.
echo %DATE% %TIME%
echo.

