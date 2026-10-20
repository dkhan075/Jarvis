@echo off
REM Build Jarvis into dist\Jarvis\Jarvis.exe
REM   build.bat            -> with a console window (use this first, errors are visible)
REM   build.bat windowed   -> no console window (final version)

set WINDOW=
if "%1"=="windowed" set WINDOW=--windowed

pyinstaller --noconfirm --clean --onedir --name Jarvis %WINDOW% ^
  --hidden-import pyttsx3.drivers ^
  --hidden-import pyttsx3.drivers.sapi5 ^
  --collect-all speech_recognition ^
  --collect-data gtts ^
  --collect-submodules google.genai ^
  gui_main.py

echo.
echo Done. Copy your .env file into dist\Jarvis\ next to Jarvis.exe, then run it.
pause