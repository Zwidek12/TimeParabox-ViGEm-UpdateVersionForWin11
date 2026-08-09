@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Challenge 29 ===
echo Enter Challenge 29 (Restart if needed), then focus the game.
pause
TimeParabox.exe --extra Challenge 29 %*
pause
