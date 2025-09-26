import dns.resolver


def run_scanner(domain: str):
    print(f"[+] Starting scan for {domain}...")
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        for rdata in answers:
            print(f"CNAME record found: {rdata.to_text()}")
    except Exception as e:
        print(f"No CNAME found for {domain}: {e}")
    print(f"[+] Scan complete for {domain}")

