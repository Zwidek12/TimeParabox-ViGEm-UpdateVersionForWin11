@echo off
cd /d "%~dp0"
dotnet publish TimeParabox\TimeParabox.csproj -c Release -o publish --self-contained false
if errorlevel 1 (
  echo Build failed. Install .NET 8 SDK: https://dotnet.microsoft.com/download/dotnet/8.0
  pause
  exit /b 1
)
echo.
echo OK - output: publish\TimeParabox.exe
pause
