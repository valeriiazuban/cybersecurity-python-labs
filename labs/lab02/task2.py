import argparse
import csv
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

SEVERITY_ORDER = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Аналізатор логів EDR")
    parser.add_argument("--edr-log", required=True, help="Шлях до JSON-файлу логів EDR")
    parser.add_argument(
        "--min-severity",
        choices=["Low", "Medium", "High", "Critical"],
        default="Low",
        help="Мінімальний рівень критичності для аналізу",
    )
    parser.add_argument("--out-csv", help="Шлях для збереження підсумкового CSV-звіту")
    parser.add_argument(
        "--log-file", help="Шлях до файлу для збереження системних логів"
    )
    return parser


def setup_logging(log_file: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
        except OSError as e:
            logger.error("Не вдалося створити лог-файл %s: %s", log_file, e)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=handlers,
    )


def process_edr_logs(
    edr_log_path: Path, min_severity: str
) -> tuple[dict, list[dict], list[tuple[str, int]]]:
    if not edr_log_path.exists():
        logger.error("Файл журналів %s не знайдено!", edr_log_path)
        return {"total": 0, "distribution": Counter()}, [], []

    data = []
    try:
        with edr_log_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Помилка парсингу JSON файлу %s: %s", edr_log_path, e)
        return {"total": 0, "distribution": Counter()}, [], []
    except OSError as e:
        logger.error("Помилка зчитування файлу %s: %s", edr_log_path, e)
        return {"total": 0, "distribution": Counter()}, [], []
    except Exception as e:
        logger.error("Непередбачувана помилка під час обробки логів: %s", e)
        return {"total": 0, "distribution": Counter()}, [], []

    min_level = SEVERITY_ORDER.get(min_severity, 1)
    total_events = len(data)
    severity_counts = Counter()
    unresolved_threats = []
    host_threat_counts = defaultdict(int)

    for event in data:
        if not isinstance(event, dict):
            continue
        sev = event.get("Severity", "Low")
        severity_counts[sev] += 1
        if SEVERITY_ORDER.get(sev, 1) >= min_level:
            action = event.get("ActionTaken", "")
            if action not in ("Quarantined", "Deleted"):
                unresolved_threats.append(event)
            host_threat_counts[event.get("Hostname", "Unknown")] += 1

    top_hosts = sorted(host_threat_counts.items(), key=lambda x: x[1], reverse=True)
    return (
        {"total": total_events, "distribution": severity_counts},
        unresolved_threats,
        top_hosts,
    )


def export_to_csv(unresolved_threats: list[dict], output_csv_path: Path) -> None:
    fieldnames = [
        "AlertID",
        "Timestamp",
        "Hostname",
        "ThreatName",
        "Severity",
        "ActionTaken",
    ]
    try:
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with output_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in unresolved_threats:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
        logger.info("Агрегований звіт успішно збережено у %s", output_csv_path)
    except OSError as e:
        logger.error("Не вдалося зберегти звіт у CSV: %s", e)
    except Exception as e:
        logger.error("Помилка під час запису CSV: %s", e)


def analyze(args: argparse.Namespace) -> None:
    setup_logging(args.log_file)
    edr_path = Path(args.edr_log)
    logger.info("Aggregating EDR alerts from %s...", edr_path)

    stats, unresolved, _top_hosts = process_edr_logs(edr_path, args.min_severity)

    if stats["total"] == 0:
        logger.warning("Не вдалося обробити жодної події EDR.")
        return

    logger.info("Processed %d antivirus incident events.\n", stats["total"])

    print("=== Severity Distribution ===")
    for sev in ["Critical", "High", "Medium", "Low"]:
        print(f"{sev:<8}: {stats['distribution'].get(sev, 0)}")
    print()

    print("=== Unresolved Security Threats (Action Not Quarantined/Deleted) ===")
    if not unresolved:
        print("No unresolved security threats found.")
    else:
        for threat in unresolved:
            sev_str = f"[{threat.get('Severity', '').upper()}]"
            host = threat.get("Hostname", "")
            threat_name = threat.get("ThreatName", "")
            action = threat.get("ActionTaken", "")
            print(
                f"{sev_str:<10} Host: {host:<13} | Threat: {threat_name:<25} | Action: {action}"
            )
            if threat.get("Severity") in ["High", "Critical"]:
                logger.error(
                    "Unresolved alert! Host: %s, Threat: %s, Action: %s",
                    host,
                    threat_name,
                    action,
                )
    print()

    if getattr(args, "out_csv", None):
        export_to_csv(unresolved, Path(args.out_csv))
