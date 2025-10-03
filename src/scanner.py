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
import requests
import json
import datetime
from pathlib import Path
import traceback

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up one level to project root
DOMAINS_FILE = BASE_DIR / "domains.txt"
LOG_DIR = BASE_DIR / "scanner_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
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
    try:
        answers = dns.resolver.resolve(domain, 'CNAME', raise_on_no_answer=False)
        for r in answers:
            # r.target is a dns.name.Name object; convert to string
            cname = str(r.target).rstrip('.')  # remove trailing dot
            return cname
        # If no CNAME answer, return None
        return None
    except Exception as e:
        log(f"[ERROR] DNS lookup {domain}: {e}")
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
def read_domains():
    if not DOMAINS_FILE.exists():
        log(f"[WARN] domains file not found at {DOMAINS_FILE}. Creating example file.")
        DOMAINS_FILE.write_text("va01.example.herokuapp.com\nexample.azure.com\nexample.com\n", encoding="utf-8")
    with open(DOMAINS_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return lines

def run_scan():
    log("Scanner run started")
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

    log("Scanner run completed")
    return results

# Legacy function names for compatibility
def run_bulk_scan():
    """Legacy function name - calls the new run_scan function"""
    return run_scan()

if __name__ == "__main__":
    run_scan()
