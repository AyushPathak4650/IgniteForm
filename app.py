import os
from dotenv import load_dotenv
import gspread
import smtplib
from email.message import EmailMessage
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from googleapiclient.discovery import build
from email.utils import make_msgid
import re

# Load environment variables
load_dotenv()

# Fetch environment variables
sender_login = os.getenv('SMTP_LOGIN')
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SMTP_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER', 'smtp-relay.brevo.com')
smtp_port = int(os.getenv('SMTP_PORT', 587))
google_sheet_url = os.getenv('GOOGLE_SHEET_URL')
qr_code_dir = os.getenv('QR_CODE_DIR', 'qr_codes')

# Create the 'qr_codes' directory if it doesn't exist
if not os.path.exists(qr_code_dir):
    os.makedirs(qr_code_dir)

# Define the scope of access
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

# Authenticate using the service account credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('igniteform-project-f1dc7b47f1e0.json', scope)
client = gspread.authorize(creds)

# Build the Drive service
drive_service = build('drive', 'v3', credentials=creds)

# Open your Google Sheet
sheet = client.open_by_url(google_sheet_url).sheet1

# Define the Unique ID column (Column 10)
unique_id_col = 10

# Fetch all values
all_values = sheet.get_all_values()

# Fetch all existing Unique IDs
uid_col_values = sheet.col_values(unique_id_col)
existing_numbers = [int(uid.split('-')[1]) for uid in uid_col_values[1:] if uid]
current_max = max(existing_numbers) if existing_numbers else 0

# Email regex for validation
email_regex = r"[^@]+@[^@]+\.[^@]+"

# Loop through responses, start from 2 (skip header)
for i in range(2, len(all_values) + 1):
    uid_value = sheet.cell(i, unique_id_col).value
    if not uid_value:
        current_max += 1
        new_uid = f"IGN-{current_max:03}"
        sheet.update_cell(i, unique_id_col, new_uid)
        print(f"✅ Unique ID {new_uid} added to row {i}")

        name = sheet.cell(i, 2).value  # Name (Col 2)
        email = sheet.cell(i, 9).value  # Email (Col 9)

        if not name or not name.strip():
            continue
        if not email or not email.strip():
            continue
        if not re.match(email_regex, email):
            continue

        # QR code data
        qr_data = f"UID: {new_uid} | Name: {name} | Email: {email}"
        qr = qrcode.make(qr_data)
        qr_filename = os.path.join(qr_code_dir, f"{new_uid}_qr.png")
        qr.save(qr_filename)

        # Create email message
        msg = EmailMessage()
        msg['Subject'] = "Ignite Event Registration Confirmation"
        msg['From'] = f"Ignite Event <{sender_login}>"
        msg['To'] = email

        image_cid = make_msgid(domain='ignitefare.tech')[1:-1]

        html_body = f"""
        <html>
            <body>
                <h3>Hello {name},</h3>
                <p>You are successfully registered for Ignite!</p>
                <p><strong>Your Unique ID:</strong> {new_uid}</p>
                <p>Your QR code is below — please keep it safe and show it at the event entry.</p>
                <p><img src="cid:{image_cid}" alt="QR Code" style="width:200px;height:200px;"/></p>
                <br>
                <p>Regards,<br>Ignite Team</p>
            </body>
        </html>
        """

        msg.add_alternative(html_body, subtype='html')

        with open(qr_filename, 'rb') as img:
            msg.get_payload()[0].add_related(
                img.read(),
                maintype='image',
                subtype='png',
                cid=f"<{image_cid}>"
            )

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                print(f"✅ Email sent successfully to {email}")
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")

        os.remove(qr_filename)

print("✅ All emails sent successfully!")
