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
college_email = os.getenv('COLLEGE_EMAIL')
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

# Fetch all values
all_values = sheet.get_all_values()

# Fetch the header row to dynamically map column indices
header_row = sheet.row_values(1)
header_map = {header: index + 1 for index, header in enumerate(header_row)}

# Define the Unique ID column dynamically
unique_id_col = header_map.get("Unique ID")

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

        # Dynamically fetch column values using header names
        name = sheet.cell(i, header_map.get("Student Full Name")).value
        email = sheet.cell(i, header_map.get("Email Address")).value

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
        msg['Reply-To'] = college_email
        msg['Bcc'] = college_email
        msg['Subject'] = "Ignited Event Registration Confirmation"
        msg['From'] = f"Ignited Event <{sender_login}>"
        msg['To'] = email

        image_cid = make_msgid(domain='ignitefare.tech')[1:-1]

        html_body = f"""
                    <html>
                    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f4f8; padding: 15px; color: #333;">
                        <div style="width: 100%; max-width: 620px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); box-sizing: border-box;">
                        
                        <h2 style="text-align: center; color: #ff6b35; font-size: 28px; margin-bottom: 20px;">🎓 Ignited — Registration Successful!</h2>
                        
                        <p style="font-size: 16px; line-height: 1.6;">Hi <strong>{name}</strong>,</p>

                        <p style="font-size: 16px; line-height: 1.6;">Congratulations! You're officially registered for <strong>Ignited — The Education Fair</strong>. Get ready for an exciting day filled with workshops, games, free goodies, and a chance to connect with top universities and mentors!</p>

                        <div style="background-color: #fef3c7; padding: 12px 18px; border-left: 5px solid #facc15; border-radius: 8px; margin: 20px 0;">
                            <p style="font-size: 16px; margin: 0;"><strong>Your Unique ID:</strong> <span style="background-color: #facc15; color: #111827; padding: 5px 10px; border-radius: 5px;">{new_uid}</span></p>
                        </div>

                        <p style="font-size: 16px; line-height: 1.6;">Keep this ID handy — you'll need it to enter the event and participate in activities.</p>

                        <div style="text-align: center; margin: 30px 0;">
                            <p style="font-size: 16px; margin-bottom: 10px;">📸 Scan your event QR code at the entry:</p>
                            <img src="cid:{image_cid}" alt="QR Code" style="max-width: 100%; height: auto; border: 2px solid #ddd; border-radius: 10px;"/>
                        </div>

                        <p style="font-size: 16px;">We can't wait to meet you there! 🚀</p>

                        <p style="font-size: 16px; margin-top: 30px;">Cheers,<br><strong>The Ignited Team</strong></p>

                        </div>
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
