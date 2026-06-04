$ErrorActionPreference = "Stop"

Write-Host "[1/4] Installiere Build-Abhaengigkeiten..."
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

Write-Host "[2/4] Baue Windows-EXE mit PyInstaller..."
python -m PyInstaller --noconfirm --clean --onefile --name speedtest_logger speedtest_logger.py

Write-Host "[3/4] Pruefe Inno Setup..."
$innoPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

$iscc = $null
foreach ($candidate in $innoPaths) {
    if (Test-Path $candidate) {
        $iscc = $candidate
        break
    }
}

if (-not $iscc) {
    throw "Inno Setup wurde nicht gefunden. Bitte Inno Setup 6 installieren: https://jrsoftware.org/isdl.php"
}

Write-Host "[4/4] Baue Installer (.exe)..."
& $iscc "installer\windows\SpeedtestLogger.iss"

Write-Host "Fertig. Installer liegt in dist\installer\"
