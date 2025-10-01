import requests
import yaml


def load_config(path: str = "config/config.yaml") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"[!] Config file not found at {path}")
        return {}


def send_telegram_message(message: str):
    config = load_config()
    token = config.get("notifications", {}).get("telegram_token")
    chat_id = config.get("notifications", {}).get("telegram_chat_id")

    if not token or not chat_id:
        print("[!] Telegram token or chat_id not configured.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=payload)
        # Debug print of raw Telegram API response
        print("[+] Telegram Response:", response.text)
        if response.status_code == 200:
            print("[+] Telegram notification sent.")
        else:
            print(f"[!] Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        print(f"[!] Telegram error: {e}")


# Optional: function with the requested name that uses the same logic
def send_telegram(message: str):
    """Compatibility wrapper that sends a Telegram message using config values."""
    send_telegram_message(message)
