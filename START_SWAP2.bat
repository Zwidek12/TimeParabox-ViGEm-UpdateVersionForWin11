@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" call BUILD.bat
cd publish
echo === ONE-SHOT: Swap 2 ===
echo Any%% skips this level. Enter Swap 2 (clean start / Restart), then:
echo focus the game after Enter.
echo NO smoke test - waits 2s then solves.
pause
TimeParabox.exe --extra Swap 2
pause
