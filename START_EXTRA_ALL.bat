@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === EXTRA-ALL playlist (242 challenge / side / appendix / Challenge / Gallery) ===
echo You enter each puzzle. Bot solves after you press Enter in this console.
echo Resume examples:
echo   START_EXTRA_ALL.bat Challenge
echo   START_EXTRA_ALL.bat Challenge 35
echo   START_EXTRA_ALL.bat Inf Exit 4
echo   START_EXTRA_ALL.bat --delay 50 Clone
echo.
echo Keys during run: Enter = solve ^| S = skip ^| Q = quit
echo.
pause
TimeParabox.exe --extra-all %*
pause
