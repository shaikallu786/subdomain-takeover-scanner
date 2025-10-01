from scanner import run_all_scans
import schedule
import time


def job():
    print("[+] Running scheduled scan...")
    run_all_scans()
    print("[+] Scan finished.")


if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    print("[+] Real-Time Scanner with DB started.")
    while True:
        schedule.run_pending()
        time.sleep(1)
