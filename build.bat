@echo off
echo Building Wake-on-LAN...
pip install pyinstaller >nul 2>&1
pyinstaller --onefile --windowed --name "WakeOnLAN" --icon NONE wol.py
echo.
echo Done! Find WakeOnLAN.exe in the dist\ folder.
pause
