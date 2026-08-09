@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Challenge 35 ===
echo Enter Challenge 35 (Restart if needed), then focus the game.
pause
TimeParabox.exe --extra Challenge 35 %*
pause
