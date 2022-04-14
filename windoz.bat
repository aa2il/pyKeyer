@echo off
echo.
echo Notes about how to run pyKeyer on Windoze 10
echo.
echo Need the following standard Python libraries:
echo    scipy       - referenced in sig_proc library
echo    levenshtein - For computing string distance metrics
echo.
echo pip install scipy levenshtein
echo.
echo To compile - this can take a while:
echo     Spews a bunch of errors but works any ways
echo.
echo pyinstaller --onefile pyKeyer.py
echo.
echo To run (example):
echo.
echo pyKeyer -prac -sidetone -cwt -adjust -wpm 30
dist\pyKeyer -prac -sidetone -cwt -adjust -wpm 30
echo.
echo Known issue(s):
echo 1. Splash not working on windoze (low priority(
echo.
   
