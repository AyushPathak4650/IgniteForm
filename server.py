from flask import Flask, request
import subprocess
from datetime import datetime

app = Flask(__name__)

# Simple in-memory logs list
logs = []


@app.route('/')
def home():
    return "Server is running!"

# Route to display logs
@app.route('/logs')
def show_logs():
    return "<br>".join(logs) or "No logs yet."

# Route to trigger your script
@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = subprocess.run(
            ["python", "app.py"],
            check=True,
            text=True,
            capture_output=True
        )
        logs.append(f"[{datetime.now()}] ✅ Script executed successfully:\n{result.stdout}")
        return f"Script executed successfully:\n{result.stdout}", 200

    except subprocess.CalledProcessError as e:
        logs.append(f"[{datetime.now()}] ❌ Error occurred:\n{e.stderr}")
        return f"Error occurred:\n{e.stderr}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
