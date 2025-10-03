#!/usr/bin/env python3
"""
Subdomain takeover scanner:
- Reads domains from domains.txt
- Resolves CNAMEs
- Flags CNAMEs containing cloud providers (amazonaws, azure, heroku)
- Logs to daily timestamped log files in scanner_logs/
- Writes latest results to scans.json for the web dashboard
- Sends Telegram alerts (with debug output)
"""

import dns.resolver
import argparse
import requests
import json
import datetime
from pathlib import Path
import traceback

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up one level to project root
# README expects subdomains.txt and logs/ directory naming; keep backward compatibility
DEFAULT_INPUT_FILE = BASE_DIR / "subdomains.txt"
ALT_INPUT_FILE = BASE_DIR / "domains.txt"
LOG_DIR = BASE_DIR / "scanner_logs"
README_LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
README_LOG_DIR.mkdir(parents=True, exist_ok=True)
SCANS_JSON = BASE_DIR / "scans.json"

# Telegram — load from environment variables
import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")   # Set via environment variable
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")       # Set via environment variable

# risk providers (lowercase)
RISK_PROVIDERS = ["amazonaws", "azure", "heroku"]

# ---------------- Helpers ----------------
def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def daily_log_path():
    return LOG_DIR / f"scanner_{datetime.datetime.now().strftime('%Y%m%d')}.log"

def log(msg):
    line = f"{now_str()} - {msg}"
    print(line)
    with open(daily_log_path(), "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ---------------- DNS / Risk check ----------------
def resolve_cname(domain):
    """Resolve canonical name for a domain.
    1) Prefer explicit CNAME record.
    2) Fallback: use A-record answer's canonical_name (chasing any implicit CNAMEs).
    """
    # Try explicit CNAME first
    try:
        answers = dns.resolver.resolve(domain, 'CNAME', raise_on_no_answer=False)
        for r in answers:
            cname = str(r.target).rstrip('.')
            return cname
    except Exception as e:
        # not necessarily an error; we'll try fallback
        log(f"[DEBUG] No direct CNAME for {domain} or lookup error: {e}")

    # Fallback: query A and use canonical_name (dnspython follows CNAME chains)
    try:
        a_answers = dns.resolver.resolve(domain, 'A', raise_on_no_answer=False)
        canonical = str(getattr(a_answers, 'canonical_name', domain)).rstrip('.')
        # Only treat it as a cname if it's different from the original
        if canonical and canonical.lower() != domain.lower():
            return canonical
        return None
    except Exception as e:
        log(f"[ERROR] DNS A lookup {domain}: {e}")
        return None

def check_risk_from_cname(cname):
    if not cname:
        return "None"
    lower = cname.lower()
    for p in RISK_PROVIDERS:
        if p in lower:
            return "High"
    return "Low"

# ---------------- Telegram ----------------
def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        log("[WARN] BOT_TOKEN or CHAT_ID not set. Skipping Telegram send.")
        return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        resp = requests.post(url, data=payload, timeout=15)
        # Log API response (debug)
        log(f"[TELEGRAM] Response: {resp.status_code} - {resp.text}")
        return resp.text
    except Exception as e:
        log(f"[TELEGRAM] Exception while sending: {e}")
        return None

# ---------------- Main scanner ----------------
def read_domains(file_path: Path | None = None):
    """Read domains from a file. Defaults to README's subdomains.txt; falls back to domains.txt."""
    target_file = Path(file_path) if file_path else DEFAULT_INPUT_FILE
    if not target_file.exists() and ALT_INPUT_FILE.exists():
        target_file = ALT_INPUT_FILE
    if not target_file.exists():
        log(f"[WARN] input file not found at {target_file}. Creating example file.")
        example_content = (
            "# One domain per line\n"
            "va01.example.herokuapp.com\n"
            "example.azure.com\n"
            "example.com\n"
        )
        target_file.write_text(example_content, encoding="utf-8")
    with open(target_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return lines

def run_scan(domains: list[str] | None = None):
    log("Scanner run started")
    if domains is None:
        domains = read_domains()
    results = []
    for d in domains:
        try:
            cname = resolve_cname(d)
            risk = check_risk_from_cname(cname)
            entry = {
                "domain": d,
                "cname": cname,
                "risk": risk,
                "checked_at": now_str()
            }
            results.append(entry)
            log(f"Checked {d} -> cname={cname} risk={risk}")
            if risk == "High":
                # Create a readable message
                msg = f"🚨 High risk domain found: {d} (CNAME: {cname})"
                send_telegram(msg)
        except Exception as e:
            log(f"[ERROR] scanning {d}: {e}")
            log(traceback.format_exc())

    # Save latest scan to JSON for the web UI
    try:
        SCANS_JSON.write_text(json.dumps({"last_run": now_str(), "results": results}, indent=2), encoding="utf-8")
        log(f"Wrote {len(results)} scan results to {SCANS_JSON}")
    except Exception as e:
        log(f"[ERROR] writing scans.json: {e}")

    # Also write a simple text log per README expectations
    try:
        output_txt = README_LOG_DIR / "scan_results.txt"
        lines = [
            f"[INFO] Scanned {len(results)} domains at {now_str()}\n"
        ]
        for r in results:
            if r.get("risk") == "High":
                lines.append(f"[+] Potential takeover: {r['domain']} -> {r.get('cname') or '-'}\n")
            elif r.get("risk") == "Low":
                lines.append(f"[-] {r['domain']} -> No issues found\n")
            else:
                lines.append(f"[?] {r['domain']} -> Unknown\n")
        output_txt.write_text("".join(lines), encoding="utf-8")
    except Exception as e:
        log(f"[ERROR] writing README-style log: {e}")

    log("Scanner run completed")
    return results

# Legacy function names for compatibility
def run_bulk_scan():
    """Legacy function name - calls the new run_scan function"""
    return run_scan()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain Takeover Scanner")
    parser.add_argument("-d", "--domain", help="Scan a single domain", default=None)
    parser.add_argument("-f", "--file", help="Path to file with one domain per line (defaults to subdomains.txt)", default=None)
    args = parser.parse_args()

    domains_to_scan: list[str] | None
    if args.domain:
        domains_to_scan = [args.domain]
    else:
        domains_to_scan = read_domains(Path(args.file) if args.file else None)

    run_scan(domains_to_scan)
