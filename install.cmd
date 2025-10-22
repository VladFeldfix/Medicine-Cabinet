@echo off
set SCRIPT=Medicine-Cabinet.py
set ICON=favicon.ico

if not exist "%SCRIPT%" echo ❌ %SCRIPT% not found! & pause & exit /b

python -m pip install pyinstaller >nul
echo 🚧 Building %SCRIPT%...
pyinstaller --distpath "%cd%" --onefile --noconsole -i "%ICON%" "%SCRIPT%"

rmdir /s /q build __pycache__ >nul 2>&1
del /q "%~n0.spec" >nul 2>&1
echo ✅ Done! EXE created in: %cd%
pause
