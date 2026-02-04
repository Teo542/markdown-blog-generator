@echo off
title Markdown Blog Generator

:menu
cls
echo ========================================
echo   Markdown Blog Generator
echo ========================================
echo.
echo   1. Admin Panel (localhost:5000)
echo      Create/edit posts, upload images
echo.
echo   2. Blog Preview (localhost:8000)
echo      View the generated website
echo.
echo   3. Build Site
echo      Generate HTML from markdown
echo.
echo   4. Exit
echo.
echo ========================================
set /p choice="Select option (1-4): "

if "%choice%"=="1" goto admin
if "%choice%"=="2" goto preview
if "%choice%"=="3" goto build
if "%choice%"=="4" goto end

echo Invalid choice. Press any key to try again...
pause >nul
goto menu

:admin
cls
echo Starting Admin Panel...
echo.
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python main.py admin
pause
goto menu

:preview
cls
echo Starting Blog Preview...
echo.
echo Open your browser to: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000 -d dist
pause
goto menu

:build
cls
echo Building site...
echo.
python main.py build
echo.
echo Build complete!
pause
goto menu

:end
exit
