import requests
from db import init_db, insert_scan_result
import os
import datetime

# --- Telegram Setup ---
BOT_TOKEN = "8060633424:AAHNsnm__5hfJ5VAvm_aVULrzFh9O9a-fxE"
CHAT_ID = "5736608020"

LOG_PATH = os.path.join("logs", "scanner.log")

def log_message(msg: str) -> None:
    os.makedirs("logs", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} - {msg}\n")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        print("[+] Telegram Response:", response.text)
        log_message(f"Telegram response: {response.text}")
    except Exception as e:
        print(f"[!] Telegram Error: {e}")
        log_message(f"Telegram error: {e}")


def risk_level_for_cname(cname: str) -> str:
    cname_lc = (cname or "").lower()
    suspicious_keywords = ["amazonaws", "azure", "heroku"]
    for keyword in suspicious_keywords:
        if keyword in cname_lc:
            print(f"[!] High risk domain detected: {cname}")
            return "HIGH"
    return "LOW"


def load_config(path: str = "config/config.yaml") -> dict:
    # Not used in this simplified test version
    return {}


def run_scanner(domain: str):
    # simplified test path; DB writes handled elsewhere in this version
    log_message(f"Starting scan for {domain}")
    print(f"[+] Starting scan for {domain}...")
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        found = False
        for rdata in answers:
            cname = rdata.to_text()
            print(f"CNAME record found: {cname}")
            log_message(f"CNAME found for {domain}: {cname}")
            risk = risk_level_for_cname(cname)
            print(f"Risk Level: {risk}")
            log_message(f"Risk for {domain}: {risk}")
            if risk == "HIGH":
                send_telegram(f"🚨 High risk domain found: {cname}")
            found = True
        if not found:
            print(f"[+] No CNAME records found for {domain}")
            log_message(f"No CNAME for {domain}")
    except Exception as e:
        print(f"No CNAME found for {domain}: {e}")
    print(f"[+] Scan complete for {domain}")
    log_message(f"Scan complete for {domain}")


def run_all_scans():
    # simplified test list
    for domain in [
        "va01.ingress.herokuapp.com",
        "something.azure.com",
        "example.com",
    ]:
        run_scanner(domain)


# --- Bulk scan from domains.txt ---
from typing import Tuple, Optional
import dns.resolver
def check_cname(domain: str) -> Tuple[Optional[str], str]:
    """Resolve CNAME and determine simple risk based on provider keywords.

    If the domain has no CNAME, treat risk as LOW (common for apex domains).
    """
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        cname = answers[0].to_text()
        cname_lc = (cname or "").lower()
        if any(provider in cname_lc for provider in ["amazonaws", "azure", "heroku"]):
            return cname, "HIGH"
        return cname, "LOW"
    except Exception:
        # No CNAME or DNS error: mark as LOW instead of NOT FOUND
        return None, "LOW"


def run_bulk_scan():
    """Read domains from domains.txt, check CNAME, store results."""
    init_db()
    try:
        with open("domains.txt", "r", encoding="utf-8") as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[!] domains.txt not found.")
        return

    for domain in domains:
        print(f"[+] Scanning {domain}...")
        cname, risk = check_cname(domain)
        # Persist using existing helper (maps to risk_level column)
        insert_scan_result(domain, cname or "N/A", risk)



# --- Utility entrypoints for simulated inserts ---
def insert_scan(domain: str, cname: str, risk: str) -> None:
    """Insert a single scan row using existing DB helpers."""
    init_db()
    normalized_risk = (risk or "").upper()
    if normalized_risk not in {"HIGH", "LOW"}:
        normalized_risk = "LOW"
    insert_scan_result(domain, cname, normalized_risk)


if __name__ == "__main__":
    run_bulk_scan()
    print("[+] Bulk scan completed.")
