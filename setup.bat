@echo off
echo ============================================================
echo Pico W Web Server Setup
echo ============================================================
echo.

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo Python is installed!
echo.

echo [2/3] Installing required packages...
pip install flask requests
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    echo Try running: pip install flask requests
    pause
    exit /b 1
)
echo Packages installed!
echo.

echo [3/3] Finding your IP address...
echo.
echo Your IP address is shown below (look for "IPv4 Address"):
echo.
ipconfig | findstr /i "IPv4"
echo.
echo ============================================================
echo Setup complete!
echo.
echo To start the server, run:
echo   python server.py
echo.
echo To test the server, run (in a new window):
echo   python test_server.py
echo ============================================================
echo.
pause
