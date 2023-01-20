@echo off
rem ###########################################################################
rem #
rem # practice.bat - J.B.Attili - 2023
rem #
rem # Script showing how to start the keyer for practice.
rem #
rem ###########################################################################

set NANO=
rem set NANO=-nano

rem Pick one
set CONTEST=cwt
rem set CONTEST=sst
rem set CONTEST=mst
rem set CONTEST=naqp

rem ###########################################################################

# Start keyer
set OPTS=-prac -wpm 30 -adjust -sending %NANO% -%CONTEST%
echo OPTS=%OPTS%

set CMD="c:\Program File (x86)\pyKeyer.exe %OPTS%"
echo CMD=%CMD%
%CMD%



