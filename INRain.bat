@echo off
REM INRain launcher - run .inr / .inrain files
REM Usage: INRain myscript.inr

set SCRIPT_DIR=%~dp0

if "%~1"=="" (
    echo INRain - usage: INRain yourfile.inr
    exit /b 1
)

python "%SCRIPT_DIR%inrain.py" %*
