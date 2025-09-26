import schedule
import time
from scanner import run_all_scans


def job():
    print("[+] Running scheduled scan...")
    run_all_scans()
    print("[+] Scan finished.")


if __name__ == "__main__":
    schedule.every(5).minutes.do(job)  # scan every 5 minutes
    print("[+] Real-Time Scanner started.")
    while True:
        schedule.run_pending()
        time.sleep(1)
