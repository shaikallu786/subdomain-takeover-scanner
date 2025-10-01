import sqlite3


def init_db():
    conn = sqlite3.connect("database/scans.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            cname TEXT,
            risk_level TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_scan_result(domain: str, cname: str, risk_level: str):
    conn = sqlite3.connect("database/scans.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (domain, cname, risk_level) VALUES (?, ?, ?)
    """, (domain, cname, risk_level))
    conn.commit()
    conn.close()
