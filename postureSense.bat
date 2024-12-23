@echo off
REM Ensure Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not added to PATH.
    pause
    exit /b
)

REM Check if requirements.txt exists
IF NOT EXIST "requirement.txt" (
    echo requirements.txt not found.
    pause
    exit /b
)


REM Run the Python script
echo Running main.py...
python main.py
pause
