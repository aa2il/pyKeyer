@echo off
echo %DATE% %TIME%
goto BUILD
echo.
echo Notes about how to run pyKeyer on Windoze 10/11
echo.
echo This first section assumes you've already installed Python on windoz.
echo As of Oct 2024, Python v3.12 was directly available from the Microshaft store.
echo You will also need to clone the github repositores for the source code and libraries.
echo See the section "Installtion for Windoz" in README.md for more details.
echo.
echo We should already installed most of what we need but if not:
echo.
        pip install -r requirements.txt
echo.
echo Run the script under python (an exmaple):
echo The automatic determination of the keying device does not work (yet)
echo under windows so we have to specify the keying device, e.g.
echo.
         pyKeyer.py -prac -cwt -adjust -wpm 30 -keyer WINKEY
echo.
echo. Paddling practice also works but the keyer is hardwired to WINKEY when in windoz
echo.
         paddling.py
echo.
echo There is quick callsign lookup script also included here:
echo.
        qrz.py aa2il
echo.
echo Note: There are two modules that are used, pyudev and termios, that
echo are linux-only.  They have been disabled.
echo.
:BUILD
echo.
echo This next section details how to make an installer and executable for Windoz.
echo To compile - this takes a while and spews a bunch of errors but works anyways:
echo.
echo First, we need pyinstaller:
echo.
        pip install --upgrade pyinstaller
        pyinstaller --version
echo.
echo If this leads to a command not found error, the windoz PATH isn't setup.  See 
echo        https://pyinstaller.org/en/stable/installation.html
echo for how to go about fixing this.  Alternatively, use
echo        python -m PyInstaller
echo to invoke pyinstaller, e.g.
echo.
        python -m PyInstaller --version
echo.
echo I like the latter approach since you don't have to fiddle with the windows path.
echo.
echo Compile the code:
echo.
echo    pyinstaller --onefile pyKeyer.py
echo    pyinstaller --onefile paddling.py
echo.
echo or
echo.
        python -m PyInstaller --onefile pyKeyer.py
        python -m PyInstaller --onefile paddling.py
        python -m PyInstaller --onefile qrz.py
echo.
echo Next, copy support files into distribution directory:
         copy ..\data\cty.plist dist
         copy ..\data\cty.bin dist
         copy ..\data\master.csv dist
	 copy Book.txt dist
	 copy Panagrams.txt dist
	 copy Stumble.txt dist
	 copy QSO_Template.txt dist
	 copy keyer_splash.png dist
         copy Release_Notes.txt dist
         copy practice.bat dist
         del dist\Output\pyKeyer_setup.exe
echo.
echo On linux:
echo      cp ../data/cty.plist ../data/cty.bin Book.txt Panagrams.txt Stumble.txt QSO_Template.txt keyer_splash.png dist
echo      cp Release_Notes.txt dist practice.bat dist
echo.
echo Run compiled version (examples):
         dist\pyKeyer.exe -prac -sidetone -cwt -adjust -wpm 30
         dist\paddling.exe
         dist\qrz.exe aa2il
echo.
echo The good news:
echo     - paddling and qrz seem to work just fine
echo     - CWT practice works great!
echo     - It can find and use the nano_io!
echo     - It does find the rig and nanoIO on windows
echo.
echo Known issue(s):
echo     0. Compiled version seems just fine under linux.
echo        May need pavucontrol to direct pulse audio output.   
echo     1. Rig control and keying under windoz doesn't work (yet)
echo.
echo Run Inno Setup Compiler and follow the prompts to create installers for each app.
echo The compiler is available at jrsoftware.org.  Click on the desktop icon to start it,
echo     select the appropriate .iss file and click on the blue triangle to create each installer.
echo The resulting installers work on Windoz 10/11 and Bottles and can be found in
echo.
echo      dist\Output
echo.
echo The installers are too big to share via github so I used Scroogle Drive instead.  Open
echo Drive with a web browser and drag and drop the installers via a file browser.  
echo.
echo Be sure to include the following files:
echo      keyer_splash.png   - need to rename this to be program specific
echo      Book.txt, Panagrams.txt, Stumble.txt and QSO_Template.txt
echo      state.json
echo.
echo You can run the executables from the command via:
echo.
echo "\Program Files (x86)\AA2IL\pyKeyer.exe" -practice -cwt
echo.
echo %DATE% %TIME%
echo.

