@echo off
echo Building Mixamo Downloader...

rem Ensure we're using the virtual environment
call .venv\Scripts\activate.bat

rem Run PyInstaller with simple options
pyinstaller --onefile --windowed --icon=mixamo.ico --add-data "mixamo_anims.json;." --add-data "mixamo.ico;." main.pyw

echo Build complete. Output in dist folder.
pause 