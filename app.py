import os
from dotenv import load_dotenv
import gspread
import smtplib
from email.message import EmailMessage
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from PIL import Image
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from email.utils import make_msgid

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
sender_email = os.getenv('EMAIL_ADDRESS')  # Brevo login email
sender_password = os.getenv('EMAIL_PASSWORD')  # Brevo SMTP password
smtp_server = os.getenv('SMTP_SERVER', 'smtp-relay.brevo.com')
smtp_port = int(os.getenv('SMTP_PORT', 587))  # Default to 587 if not set
google_sheet_url = os.getenv('GOOGLE_SHEET_URL')
qr_code_dir = os.getenv('QR_CODE_DIR', 'qr_codes')  # Default to 'qr_codes' if not set

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

# Open your Google Sheet (use the Sheet's URL from environment variable)
sheet = client.open_by_url(google_sheet_url).sheet1

# Define the column number for Unique ID (Column 10)
unique_id_col = 10

# Fetch all values
all_values = sheet.get_all_values()

# Fetch all Unique IDs from the UID column
uid_col_values = sheet.col_values(unique_id_col)

# Get max existing UID number
existing_numbers = [
    int(uid.split('-')[1]) for uid in uid_col_values[1:] if uid
]

current_max = max(existing_numbers) if existing_numbers else 0

# Loop through responses, start from 2 (skip header)
for i in range(2, len(all_values) + 1):
    uid_value = sheet.cell(i, unique_id_col).value
    if not uid_value:
        # Generate a new UID
        current_max += 1
        new_uid = f"IGN-{current_max:03}"
        sheet.update_cell(i, unique_id_col, new_uid)
        print(f"✅ Unique ID {new_uid} added to row {i}")

        # Get the latest data for the current row
        name = sheet.cell(i, 2).value  # Column 2 for Name
        email = sheet.cell(i, 9).value  # Column 9 for Email

        # QR code data (You can customize the format)
        qr_data = f"UID: {new_uid} | Name: {name} | Email: {email}"

        # Generate QR code
        qr = qrcode.make(qr_data)
        qr_filename = os.path.join(qr_code_dir, f"{new_uid}_qr.png")
        qr.save(qr_filename)

        # Create email message
        msg = EmailMessage()
        msg['Subject'] = "Ignite Event Registration Confirmation"
        msg['From'] = "noreply@ignitefare.tech"  # Updated sender email
        msg['To'] = email

        # Generate a Content-ID for the image
        image_cid = make_msgid(domain='ignitefare.tech')  # You can leave domain=None too
        image_cid_clean = image_cid[1:-1]  # Remove < >

        # HTML Email body with image via CID
        msg.set_content(f"""
        <html>
            <body>
                <h3>Hello {name},</h3>
                <p>You are successfully registered for Ignite!</p>
                <p><strong>Your Unique ID:</strong> {new_uid}</p>
                <p>Your QR code is below — please keep it safe and show it at the event entry.</p>
                <p><img src="cid:{image_cid_clean}" alt="QR Code" style="width:200px;height:200px;"/></p>
                <br>
                <p>Regards,<br>Ignite Team</p>
            </body>
        </html>
        """, subtype='html')

        # Attach QR code image with Content-ID
        with open(qr_filename, 'rb') as img:
            msg.add_attachment(img.read(),
                               maintype='image',
                               subtype='png',
                               cid=image_cid)

        # Delete local QR code file
        os.remove(qr_filename)

        # Send via SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print(f"✅ Email sent successfully to {email} with embedded QR code!")
print("All emails sent successfully!")
