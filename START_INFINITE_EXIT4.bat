@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Infinite Exit 4 ===
echo Enter Infinite Exit 4 (Restart if needed), then focus the game.
pause
TimeParabox.exe --extra "Infinite Exit" 4
pause
