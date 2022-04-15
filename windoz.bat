@echo off
echo.
echo Notes about how to run pyKeyer on Windoze 10
echo.
echo Need the following standard Python libraries:
echo    scipy       - referenced in sig_proc library
echo    levenshtein - For computing string distance metrics
echo            pip install scipy levenshtein
echo.
echo To compile - this can take a while:
echo Spews a bunch of errors but works anyways
echo            pyinstaller --onefile pyKeyer.py
echo.
echo To run (example):
echo.
echo pyKeyer -prac -sidetone -cwt -adjust -wpm 30
echo dist\pyKeyer -prac -sidetone -cwt -adjust -wpm 30
echo.
echo Known issue(s):
echo 1. Splash not working on windoze (low priority(
echo 2. Hanve't tested rig control and keying under windoz
echo 3. Doesn't find nanoIO on windows
echo 4. Startup need some sort of flag - need to go into practice mode
echo    on windoz since we can't find rig anyway
echo 5. Requires Python/history/data/master.csv - need to rethink where we store things
echo.
echo Run Inno Setup Compiler & follow the prompts to create an installer
echo This installer works on Windoz 10 & Bottles!
echo Be sure to include the following files:
echo      splash.png   - need to rename this to be program specific
echo      Pnagrams.txt, Stumble.txt & QSO_Template.txt
echo.

