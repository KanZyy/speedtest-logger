# Speedtest Logger

Dieses Projekt kann als portable Windows-EXE gebaut werden, ohne dass auf dem Zielsystem Python installiert sein muss.

## Windows-EXE bauen (lokal auf Windows)

Voraussetzungen:
- Python 3.11+

Befehle in PowerShell im Projektordner:

```powershell
./build_windows_exe.ps1
```

Ergebnis:
- EXE: `dist/speedtest_logger.exe`

Die EXE kann direkt an deinen Kollegen weitergegeben werden.

## Windows-EXE bauen (GitHub Actions)

Workflow:
- `.github/workflows/windows-exe.yml`

Start:
1. Repository pushen.
2. In GitHub unter Actions den Workflow `Build Windows EXE` starten.
3. Option `publish_release` auf `true` lassen.
4. Nach Abschluss unter Releases die neu erzeugte Version oeffnen.
5. Datei `speedtest_logger.exe` herunterladen und weitergeben.

Alternative:
- Falls du keine Release willst, kannst du weiterhin das Artefakt `speedtest_logger_exe` aus dem Workflow herunterladen.

## Optional: Installer bauen

Wenn du spaeter doch einen klassischen Setup-Installer willst:
- Script: `build_windows_installer.ps1`
- Workflow: `.github/workflows/windows-installer.yml`

## Hinweis zur Laufzeit

Die gebaute EXE bringt den Python-Interpreter mit. Auf dem Zielsystem ist keine separate Python-Installation notwendig.
