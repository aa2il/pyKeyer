@echo off
echo.
echo Notes about how to run pyKeyer on Windoze 10
echo.
echo Need the following standard Python libraries:
echo    scipy       - referenced in sig_proc library
echo    levenshtein - For computing string distance metrics
echo            pip install scipy levenshtein
echo.
echo To compile - this can take a while - Spews a bunch of errors but works anyways:
echo.
echo     pyinstaller --onefile pyKeyer.py
echo.
echo To run (example):
echo.
echo     pyKeyer.py -prac -sidetone -cwt -adjust -wpm 30
echo     dist\pyKeyer.exe -prac -sidetone -cwt -adjust -wpm 30
echo.
echo Known issue(s):
echo     0. Compiled version seems just fine under linux.
echo        May need pavucontrol to direct pulse audio output.   
echo     1. Splash not working on windoze (low priority(
echo     2. Have't tested rig control and keying under windoz - probably doesn't work
echo     3. Doesn't find nanoIO on windows
echo.
echo Run Inno Setup Compiler & follow the prompts to create an installer
echo This installer works on Windoz 10 & Bottles!
echo Be sure to include the following files:
echo      keyer_splash.png   - need to rename this to be program specific
echo      Book.txt, Panagrams.txt, Stumble.txt & QSO_Template.txt
echo.

