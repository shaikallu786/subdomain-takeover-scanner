#!/usr/bin/env python3
"""
Helper to show getUpdates output and extract chat_id.
Usage:
1. Message your bot from your Telegram account (any text).
2. Run this script (after setting BOT_TOKEN).
3. Copy chat id, then paste into scanner.py CHAT_ID.
"""
import requests, json

import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set via environment variable

def main():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(url, timeout=10)
    print("Raw response:")
    print(r.text)
    try:
        j = r.json()
        if j.get("ok") and j.get("result"):
            print("\nFound messages. Extracting chat ids:")
            for upd in j["result"]:
                msg = upd.get("message") or upd.get("edited_message")
                if not msg:
                    continue
                chat = msg.get("chat", {})
                print(chat.get("id"), "-", chat.get("username") or chat.get("first_name"))
        else:
            print("\nNo updates found. Make sure you have sent a message to the bot from Telegram.")
    except Exception as e:
        print("Error parsing response:", e)

if __name__ == "__main__":
    main()
