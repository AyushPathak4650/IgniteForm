# 🎓 Ignited Event Registration System 

An automated Python + Flask backend system to manage event registrations via Google Sheets — assigning unique participant IDs, generating QR codes, and sending confirmation emails with QR codes attached.  

---

## 📂 Repository Structure

```

ignite-registration-system/  
├── .gitignore  
├── .env # Environment variables (excluded from git)  
├── .env.example # Example environment file  
├── igniteform-project-xxxxx.json # Google Service Account credentials (excluded from git)  
├── app.py # Main registration processor  
├── server.py # Flask server to trigger and view logs  
├── requirements.txt # Python dependencies  
├── qr_codes/ # Temp QR images (auto-deleted; ignored in git)  
└── README.md # This file

```

---

## 🚀 Setup Instructions

### 1️⃣ Clone & Install Dependencies
```bash
git clone https://github.com/AyushPathak4650/IgniteForm.git
cd IgniteForm
python3 -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

* * *

### 2️⃣ Environment Variables

* Copy `.env.example` to `.env`
    

```bash
cp .env.example .env
```

* Fill in actual values in `.env`  
    (see `.env.example` for required variables)
    

* * *

### 3️⃣ Google Service Account Credentials

* Place your service account key JSON file (e.g. `igniteform-project-xxxxx.json`) in the project root.
    
* It must have access to your target Google Sheet and "Google Drive API" enabled.
    

* * *

### 4️⃣ Run Flask Server

```bash
python server.py
```

Visit:

* `http://localhost:5000/` — Server status
    
* `http://localhost:5000/logs` — Execution logs
    

* * *

### 5️⃣ Trigger Registration Script

Send a POST request to run `app.py`:

```bash
curl -X POST http://localhost:5000/run-script
```

Or trigger via a browser POST extension (like Postman).

* * *

## 📡 Key Features

✅ Reads new form submissions from Google Sheets  
✅ Assigns a unique ID (`IGN-001` etc.)  
✅ Generates participant QR codes  
✅ Sends confirmation emails with embedded QR codes via Brevo SMTP  
✅ Web interface to view logs  
✅ Secure `.env` config and Google API credential management

* * *

## 📦 Dependencies

See `requirements.txt` for all packages:

* Flask
    
* python-dotenv
    
* gspread
    
* oauth2client
    
* google-api-python-client
    
* qrcode
    
* requests
    

* * *

## 📄 Notes

* `.env` and `igniteform-project-xxxxx.json` are **not committed to GitHub** (see `.gitignore`)
    
* QR images are stored temporarily in `qr_codes/` and auto-deleted after email dispatch
    

* * *

## 📄 License

MIT License — free to use and customize ✌️

* * *

## ✨ Built with ❤️ by [AyushPathak4650](https://github.com/AyushPathak4650)