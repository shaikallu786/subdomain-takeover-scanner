import dns.resolver
import yaml


def run_scanner(domain: str):
    print(f"[+] Starting scan for {domain}...")
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        for rdata in answers:
            print(f"CNAME record found: {rdata.to_text()}")
    except Exception as e:
        print(f"No CNAME found for {domain}: {e}")
    print(f"[+] Scan complete for {domain}")

def load_config(path: str = "config/config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data
    except FileNotFoundError:
        return {}

def run_all_scans():
    config = load_config()
    domains = config.get("scan", {}).get("target_domains", [])
    for domain in domains:
        run_scanner(domain)
