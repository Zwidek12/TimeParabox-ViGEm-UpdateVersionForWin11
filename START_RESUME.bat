@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo Resume: enter the puzzle manually first, then type e.g. Eat 2
set /p ARGS="Hub [number]: "
if "%ARGS%"=="" exit /b 1
pause
TimeParabox.exe %ARGS%
pause
