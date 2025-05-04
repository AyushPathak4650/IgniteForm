from flask import Flask, request
import subprocess

app = Flask(__name__)

# Define the route to trigger your script
@app.route('/run-script', methods=['POST'])
def run_script():
    try:
        # Running the script using the system Python interpreter
        subprocess.run(["python", "app.py"], check=True)
        return "Script executed successfully", 200
    except subprocess.CalledProcessError as e:
        return f"Error occurred: {str(e)}", 500

if __name__ == '__main__':
    # If you deploy on Render, it will use the correct WSGI setup
    app.run(host='0.0.0.0', port=5000)
