echo Hey 1

echo me=%~n0
echo log=%TEMP%\%me%.txt

goto DONE

goto CLOCK
cd "c:\Program Files (x86)\flrig-1.4.7\"
start flrig.exe

echo Hey 2
cd %USERPROFILE%\Python\pyKeyer
:: start pyKeyer.py -rig FLRIG
:: cd dist
:: pyKeyer.exe -rig FLRIG

:CLOCK
cd %USERPROFILE%\Python\
del CLOCK
start cmd /c wclock\dist\wclock.exe ^> CLOCK
:: start call wclock\dist\wclock.exe ^1^> CLOCK ^2^>^&^1
:: start cmd /c ^( wclock\dist\wclock.exe ^1^> CLOCK ^2^>^&^1 ^)

:DONE
:: exit



