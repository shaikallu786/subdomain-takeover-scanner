from flask import Flask, render_template, send_from_directory
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent  # Go up one level to project root
SCANS_JSON = BASE_DIR / "scans.json"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))

@app.route("/")
def index():
    scans = {"last_run": "never", "results": []}
    if SCANS_JSON.exists():
        try:
            scans = json.loads(SCANS_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            scans = {"last_run": "error", "results": [], "error": str(e)}
    return render_template("index.html", scans=scans)

@app.route("/logs/<path:filename>")
def logs(filename):
    logs_dir = BASE_DIR / "scanner_logs"
    return send_from_directory(str(logs_dir), filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)