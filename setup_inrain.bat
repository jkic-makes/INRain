@echo off
REM Run this ONCE (as normal or admin) to make "INRain" work from any folder,
REM as long as this USB stays plugged in with the same drive letter.

set SCRIPT_DIR=%~dp0

echo Adding %SCRIPT_DIR% to your PATH for this user...
setx PATH "%PATH%;%SCRIPT_DIR%"

echo.
echo Done! Close and reopen CMD, then you can just cd anywhere and type:
echo     INRain myscript.inr
echo.
pause
