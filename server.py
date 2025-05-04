from flask import Flask, request
import subprocess

app = Flask(__name__)


@app.route('/run-script', methods=['POST'])
def run_script():
    # Use the correct virtual environment's Python interpreter
    subprocess.run(["D:\\AYUSH_BACKUPFILES\\OneDrive\\Documents\\VS Code\\git\\Ignite_Project\\.venv\\Scripts\\python.exe", "app.py"])
    return "Script executed successfully", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)