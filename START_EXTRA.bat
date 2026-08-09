@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === EXTRA puzzles (challenge / side / appendix) ===
echo 1. Open level select, enter the puzzle manually
echo 2. Type hub + number, e.g.:
echo      Enter 5
echo      Eat 13
echo      "Appendix: Priority" 2
echo      Challenge 1
echo.
echo List all: TimeParabox.exe --list-extra
echo.
set /p ARGS="Hub + id: "
if "%ARGS%"=="" exit /b 1
pause
TimeParabox.exe --extra %ARGS%
pause
