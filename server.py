from flask import Flask, request
import subprocess

app = Flask(__name__)

# Define the route to trigger your script
@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        # Capture stdout and stderr
        result = subprocess.run(
            ["python", "app.py"],
            check=True,
            text=True,
            capture_output=True
        )
        return f"Script executed successfully: {result.stdout}", 200
    except subprocess.CalledProcessError as e:
        # Log the error output
        return f"Error occurred: {e.stderr}", 500

if __name__ == '__main__':
    # If you deploy on Render, it will use the correct WSGI setup
    app.run(host='0.0.0.0', port=5000)
