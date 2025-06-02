from flask import Flask, request
import subprocess
from datetime import datetime
import re

app = Flask(__name__)

# Simple in-memory logs list
logs = []

# Function to partially mask email addresses in logs
def mask_sensitive_info(log_content):
    # Partially mask email addresses (e.g., "exa***@domain.com")
    masked_content = re.sub(
        r'([a-zA-Z0-9._%+-]{3})[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'\1***\2',
        log_content
    )
    return masked_content


@app.route('/')
def home():
    return "Server is running!"

# Route to display logs
@app.route('/logs')
def show_logs():
    return "<br>".join(logs) or "No logs yet."

# Route to trigger script
@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = subprocess.run(
            ["python", "app.py"],
            check=True,
            text=True,
            capture_output=True
        )
        sanitized_stdout = mask_sensitive_info(result.stdout)
        logs.append(f"[{datetime.now()}] ✅ Script executed successfully:\n{sanitized_stdout}")
        return f"Script executed successfully:\n{sanitized_stdout}", 200

    except subprocess.CalledProcessError as e:
        sanitized_stderr = mask_sensitive_info(e.stderr)
        logs.append(f"[{datetime.now()}] ❌ Error occurred:\n{sanitized_stderr}")
        return f"Error occurred:\n{sanitized_stderr}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
