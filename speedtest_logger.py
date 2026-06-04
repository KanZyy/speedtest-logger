#!/usr/bin/env python3
"""
Führt alle 10 Minuten einen Netzwerk-Speedtest aus und speichert die Ergebnisse.

Gemessene Werte:
- Ping in ms
- Download in Mbit/s (Megabit pro Sekunde)
- Upload in Mbit/s (Megabit pro Sekunde)

Logformat (CSV):
timestamp_iso8601,ping_ms,download_mbit_s,upload_mbit_s,hinweis
"""

from __future__ import annotations

import argparse
import csv
import json
import signal
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def now_filename_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def ensure_log_header(log_path: Path) -> None:
    if log_path.exists() and log_path.stat().st_size > 0:
        return

    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp_iso8601",
                "ping_ms",
                "download_mbit_s",
                "upload_mbit_s",
                "hinweis",
            ]
        )


def make_session_log_path(base_log_path: Path, start_stamp: str) -> Path:
    return base_log_path.with_name(
        f"{base_log_path.stem}_{start_stamp}_bis_running{base_log_path.suffix}"
    )


def finalize_log_path(active_log_path: Path, end_stamp: str) -> Path:
    running_marker = "_bis_running"
    final_name = active_log_path.name
    if running_marker in final_name:
        final_name = final_name.replace(running_marker, f"_bis_{end_stamp}")
        final_log_path = active_log_path.with_name(final_name)
        active_log_path.rename(final_log_path)
        return final_log_path
    return active_log_path


def format_connection_error(exc: Exception) -> str:
    base_text = "Keine Verbindung: Speedtest konnte nicht aufgezeichnet werden"

    if isinstance(exc, subprocess.TimeoutExpired):
        return f"{base_text} (Zeitlimit ueberschritten)"

    if isinstance(exc, subprocess.CalledProcessError):
        return f"{base_text} (Tool meldete einen Fehler)"

    if isinstance(exc, json.JSONDecodeError):
        return f"{base_text} (ungueltige Tool-Ausgabe)"

    return f"{base_text} ({exc})"


def detect_backend() -> str:
    speedtest_cmd = shutil.which("speedtest")
    if speedtest_cmd:
        try:
            version_proc = subprocess.run(
                ["speedtest", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            version_text = (version_proc.stdout + "\n" + version_proc.stderr).lower()
            if "speedtest-cli" in version_text:
                return "speedtest_cli"
        except Exception:
            pass
        return "ookla"
    if shutil.which("speedtest-cli"):
        return "speedtest_cli"

    try:
        import speedtest  # type: ignore

        _ = speedtest
        return "python_module"
    except Exception:
        return "none"


def parse_json_output(raw_output: str) -> dict:
    text = raw_output.strip()
    if not text:
        raise ValueError("Leere Ausgabe vom Speedtest-Tool")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Manche CLIs schreiben Fortschritt/Status vor die JSON-Zeile.
    for line in reversed(text.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and first < last:
        candidate = text[first : last + 1]
        return json.loads(candidate)

    raise ValueError("Keine gültige JSON-Ausgabe gefunden")


def run_speedtest(backend: str) -> tuple[float, float, float]:
    if backend == "ookla":
        proc = subprocess.run(
            ["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = parse_json_output(proc.stdout)
        ping_ms = float(data["ping"]["latency"])
        download_mbps = float(data["download"]["bandwidth"]) * 8 / 1_000_000
        upload_mbps = float(data["upload"]["bandwidth"]) * 8 / 1_000_000
        return ping_ms, download_mbps, upload_mbps

    if backend == "speedtest_cli":
        cli_cmd = "speedtest" if shutil.which("speedtest") else "speedtest-cli"
        proc = subprocess.run(
            [cli_cmd, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = parse_json_output(proc.stdout)
        ping_ms = float(data["ping"])
        download_mbps = float(data["download"]) / 1_000_000
        upload_mbps = float(data["upload"]) / 1_000_000
        return ping_ms, download_mbps, upload_mbps

    if backend == "python_module":
        import speedtest  # type: ignore

        st = speedtest.Speedtest(secure=True)
        st.get_best_server()

        download_bps = st.download()
        upload_bps = st.upload(pre_allocate=False)
        ping_ms = float(st.results.ping)

        download_mbps = download_bps / 1_000_000
        upload_mbps = upload_bps / 1_000_000
        return ping_ms, download_mbps, upload_mbps

    raise RuntimeError(
        "Kein Speedtest-Tool gefunden. Installiere eines von:\n"
        "  sudo pacman -S speedtest-cli\n"
        "  yay -S ookla-speedtest-bin\n"
        "  python -m pip install speedtest-cli"
    )


def append_log(log_path: Path, row: list[str]) -> None:
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Führt regelmäßig Speedtests aus und schreibt die Ergebnisse in eine Logdatei."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=600,
        help="Intervall in Sekunden (Standard: 600 = 10 Minuten)",
    )
    parser.add_argument(
        "--log-file",
        default="speedtest.log.csv",
        help=(
            "Basis-Pfad fuer die Logdatei. Pro Lauf wird automatisch eine neue Datei mit "
            "Start- und Endzeit im Dateinamen erzeugt."
        ),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Führt genau einen Speedtest aus und beendet sich danach.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.interval < 1:
        print("Fehler: --interval muss >= 1 sein.", file=sys.stderr)
        sys.exit(2)

    base_log_path = Path(args.log_file).expanduser().resolve()
    base_log_path.parent.mkdir(parents=True, exist_ok=True)

    start_stamp = now_filename_timestamp()
    log_path = make_session_log_path(base_log_path, start_stamp)
    ensure_log_header(log_path)

    backend = detect_backend()
    if backend == "none":
        print(
            "Fehler: Kein Speedtest-Tool gefunden.\n"
            "Installiere eines von:\n"
            "  sudo pacman -S speedtest-cli\n"
            "  yay -S ookla-speedtest-bin\n"
            "  python -m pip install speedtest-cli",
            file=sys.stderr,
        )
        sys.exit(1)

    stop = False

    def handle_stop(_signum: int, _frame) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    print("Starte Speedtest-Logger")
    print(f"Intervall: {args.interval} Sekunden")
    print(f"Logdatei (aktiver Lauf): {log_path}")
    print(f"Backend: {backend}")
    if args.once:
        print("Modus: Einmaliger Schnelltest")
    print("Beenden mit Ctrl+C")

    try:
        while not stop:
            timestamp = now_iso()

            try:
                ping_ms, download_mbps, upload_mbps = run_speedtest(backend)

                print(
                    f"[{timestamp}] Ping: {ping_ms:.2f} ms | "
                    f"Download: {download_mbps:.2f} Mbit/s | "
                    f"Upload: {upload_mbps:.2f} Mbit/s"
                )

                append_log(
                    log_path,
                    [
                        timestamp,
                        f"Ping: {ping_ms:.2f} ms",
                        f"Download: {download_mbps:.2f} Mbit/s",
                        f"Upload: {upload_mbps:.2f} Mbit/s",
                        "",
                    ],
                )

            except Exception as exc:
                connection_error = format_connection_error(exc)
                print(f"[{timestamp}] {connection_error}", file=sys.stderr)
                append_log(log_path, [timestamp, "", "", "", connection_error])

            if args.once:
                break

            if stop:
                break

            # In kleinen Schritten schlafen, damit SIGINT/SIGTERM schnell reagiert.
            remaining = args.interval
            while remaining > 0 and not stop:
                step = min(1, remaining)
                time.sleep(step)
                remaining -= step
    finally:
        end_stamp = now_filename_timestamp()
        final_log_path = finalize_log_path(log_path, end_stamp)
        if final_log_path != log_path:
            print(f"Logdatei abgeschlossen: {final_log_path}")

    print("Speedtest-Logger beendet.")


if __name__ == "__main__":
    main()
