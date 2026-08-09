@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Clone 5 (Epsilon challenge) ===
echo Enter Clone 5, Esc-Restart if needed, then focus game.
pause
TimeParabox.exe --extra Clone 5
pause
