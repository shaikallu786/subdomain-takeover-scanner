from flask import Flask, render_template, redirect, url_for
import sqlite3
import os
import subprocess
from db import init_db

# Set template directory to project root
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Initialize database when webapp starts
init_db()


def get_all_scans():
    conn = sqlite3.connect("database/scans.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


@app.route("/")
def index():
    scans = get_all_scans()
    return render_template("index.html", scans=scans)

@app.route("/run_scan")
def run_scan():
    # Run the scanner; it will insert results into the database
    subprocess.run(["python", "src/scanner.py"])  # nosec - local script execution
    # Redirect back to dashboard
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
