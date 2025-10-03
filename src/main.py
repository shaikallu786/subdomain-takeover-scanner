from scanner import run_scan
import schedule
import time


def job():
    print("[+] Running scheduled scan...")
    run_scan()
    print("[+] Scan finished.")


if __name__ == "__main__":
    schedule.every(5).minutes.do(job)
    print("[+] Real-Time Scanner with DB started.")
    while True:
        schedule.run_pending()
        time.sleep(1)
