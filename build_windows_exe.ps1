$ErrorActionPreference = "Stop"

Write-Host "[1/3] Installiere Build-Abhaengigkeiten..."
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

Write-Host "[2/3] Baue portable EXE mit PyInstaller..."
python -m PyInstaller --noconfirm --clean --onefile --name speedtest_logger --collect-all speedtest speedtest_logger.py

Write-Host "[3/3] Fertig"
Write-Host "EXE liegt hier: dist\\speedtest_logger.exe"
