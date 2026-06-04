# Speedtest Logger

Fuehrt alle 10 Minuten einen Speedtest durch und schreibt die Ergebnisse (Ping, Download, Upload) in eine CSV-Logdatei.

## Verwendung

```
speedtest_logger.exe [--interval SEKUNDEN] [--log-file PFAD] [--once]
```

| Option | Standard | Beschreibung |
|---|---|---|
| `--interval` | 600 | Messintervall in Sekunden |
| `--log-file` | `speedtest.log.csv` | Basispfad der Logdatei |
| `--once` | – | Genau einen Test ausfuehren und beenden |

Pro Sitzung wird automatisch eine neue Datei mit Start- und Endzeit im Namen angelegt, z. B. `speedtest.log_20260604-120000_bis_20260604-180000.csv`.

## Installer bauen (Windows)

Voraussetzungen:
- Python 3.11+ (inkl. `py`-Launcher)
- [Inno Setup 6](https://jrsoftware.org/isdl.php)

```powershell
./build_windows_installer.ps1
```

Ergebnis: `dist\installer\SpeedtestLoggerSetup.exe`

Der Installer bringt den Python-Interpreter mit — auf dem Zielsystem muss **nichts installiert** werden.


