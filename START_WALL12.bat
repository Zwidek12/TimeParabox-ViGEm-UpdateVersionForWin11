@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Wall 12 ===
echo Enter Wall 12 (Restart if needed), then focus the game.
pause
TimeParabox.exe --extra Wall 12
pause
