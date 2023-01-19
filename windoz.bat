rem @echo off
goto BUILD
echo %DATE% %TIME%
echo.
echo Notes about how to run pyKeyer on Windoze 10
echo.
echo Need the following standard Python libraries - these should already have been installed:
echo    scipy       - referenced in sig_proc library
echo    levenshtein - For computing string distance metrics
        pip install -r requirements.txt
echo.
echo Run the script under python (an exmaple):
         pyKeyer.py -prac -sidetone -cwt -adjust -wpm 30
echo.
:BUILD
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
echo.
echo On linux:
echo "    cp ../data/cty.plist Book.txt Panagrams.txt Stumble.txt QSO_Template.txt keyer_splash.png ~/AA2IL/master.csv dist"
echo.
echo Run compiled version (example):
         dist\pyKeyer.exe -prac -sidetone -cwt -adjust -wpm 30 -nohints
echo.
echo The good news:
echo     - CWT practice works great!
echo     - It can find and use the nano_io!
echo.
echo Known issue(s):
echo     0. Compiled version seems just fine under linux.
echo        May need pavucontrol to direct pulse audio output.   
echo     1. Splash not working on windoze (low priority(
echo     2. Have't tested rig control and keying under windoz - probably doesn't work
echo     3. Doesn't find nanoIO on windows
echo     4. Need -rig NONE on windoz - shouldnt have to do this
echo     5. Still having trouble with some chars in Book.txt - trapped for now.
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

