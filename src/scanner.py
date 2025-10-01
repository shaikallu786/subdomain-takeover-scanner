import dns.resolver
import yaml
from notifier import send_telegram_message
from db import init_db, insert_scan_result


def risk_level_for_cname(cname: str) -> str:
    suspicious_keywords = ["herokuapp", "aws", "azurewebsites", "github.io", "netlify", "surge.sh"]
    for keyword in suspicious_keywords:
        if keyword in cname:
            return "HIGH"
    return "LOW"


def load_config(path: str = "config/config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"[!] Config file not found at {path}")
        return {}


def run_scanner(domain: str):
    init_db()
    print(f"[+] Starting scan for {domain}...")
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        found = False
        for rdata in answers:
            cname = rdata.to_text()
            print(f"CNAME record found: {cname}")
            risk = risk_level_for_cname(cname)
            print(f"Risk Level: {risk}")
            insert_scan_result(domain, cname, risk)
            if risk == "HIGH":
                send_telegram_message(f"🚨 Dangling CNAME found for {domain} → {cname} (Risk: {risk})")
            found = True
        if not found:
            print(f"[+] No CNAME records found for {domain}")
    except Exception as e:
        print(f"No CNAME found for {domain}: {e}")
    print(f"[+] Scan complete for {domain}")


def run_all_scans():
    config = load_config()
    domains = config.get("scan", {}).get("target_domains", [])
    if not domains:
        print("[!] No domains found in config.")
        return
    for domain in domains:
        run_scanner(domain)
