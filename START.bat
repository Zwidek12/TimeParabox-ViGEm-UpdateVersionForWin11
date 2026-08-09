@echo off
cd /d "%~dp0"
if not exist "publish\TimeParabox.exe" (
  echo Building first...
  call BUILD.bat
)
cd publish
echo TimeParabox ViGEm - focus the game after Enter.
echo Fresh save + title screen. Settings: Enter 2x, rapid inputs ON.
pause
TimeParabox.exe %*
pause
