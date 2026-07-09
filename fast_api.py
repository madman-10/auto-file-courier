from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import smtplib
from email.message import EmailMessage
from main import process_file # Import your exact existing logic from main.py
from dotenv import load_dotenv

load_dotenv()
def send_smtp_email(recipient_email: str, file_path: str, filename: str):
    """
    Sends an email with a file attachment via SMTP.
    """
    # --- Configuration ---
    # Replace with your actual email and the App Password you generated
    SENDER_EMAIL = os.getenv("USER_EMAIL")
    APP_PASSWORD = os.getenv("USER_PASSWORD")
    
    # SMTP Server details (These are for Gmail. If using Outlook, use smtp-mail.outlook.com)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465 # Port 465 is for secure SSL connections
    
    # --- 1. Build the Email ---
    msg = EmailMessage()
    msg['Subject'] = f"Automated Delivery: {filename}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    
    # The body of your email
    msg.set_content(f"Hello,\n\nYour file '{filename}' has been processed successfully. Please find it attached to this email.\n\nBest regards,\nYour Automation System")

    # --- 2. Attach the File ---
    if not os.path.exists(file_path):
        print(f"Error: Could not find file to attach at {file_path}")
        return False

    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Determine the subtype based on file extension (defaulting to octet-stream if unknown)
    file_ext = os.path.splitext(filename)[1].lower()
    subtype = 'pdf' if file_ext == '.pdf' else 'octet-stream'
    
    if file_ext in ['.png', '.jpg', '.jpeg']:
         subtype = file_ext.replace('.', '')
         maintype = 'image'
    else:
         maintype = 'application'

    msg.add_attachment(
        file_data, 
        maintype=maintype, 
        subtype=subtype, 
        filename=filename
    )

    # --- 3. Send the Email ---
    try:
        print(f"Attempting to send email to {recipient_email}...")
        
        # Open a secure connection to the SMTP server
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            
        print("Success: Email delivered!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("Auth Error: The server rejected your login. Ensure you are using an App Password, not your standard account password.")
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
app = FastAPI()

LOCAL_INPUT_DIRECTORY = r"D:\Projects\auto-file-courier\my_local_files" 
LOCAL_OUTPUT_DIRECTORY = r"D:\Projects\auto-file-courier\processed_pdfs"

os.makedirs(LOCAL_INPUT_DIRECTORY, exist_ok=True)
os.makedirs(LOCAL_OUTPUT_DIRECTORY, exist_ok=True)

class MockUploadedFile:
    """Mimics the Streamlit UploadedFile object so main.py doesn't break."""
    def __init__(self, name, content_bytes):
        self.name = name
        self.content = content_bytes

    def read(self):
        return self.content

# Define the expected JSON payload schema from Zapier
class ZapierPayload(BaseModel):
    target_filename: str
    target_email : str

@app.post("/webhook")
async def handle_zapier_trigger(payload: ZapierPayload):
    # Grab the single variable
    raw_string = payload.target_filename
    target_filename = raw_string.replace('\\', '/').split('/')[-1].strip() + ".png"

    file_path = os.path.join(LOCAL_INPUT_DIRECTORY, target_filename)

    if not os.path.exists(file_path):
        
        # --- NEW DEBUGGING LOGIC ---
        try:
            # Tell Python to list every file it currently sees in the target folder
            files_seen = os.listdir(LOCAL_INPUT_DIRECTORY)
        except Exception as e:
            files_seen = f"Error reading directory: {e}"
        
        error_msg = (
            f"Failed to find '{target_filename}'. "
            f"Looked exactly here: '{file_path}'. "
            f"Files Python actually sees in that folder: {files_seen}"
        )
        print(error_msg) # Print to your terminal
        
        raise HTTPException(status_code=404, detail=error_msg)

    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    mock_file = MockUploadedFile(target_filename, file_bytes)
    
    # 2. Pass target_filename for BOTH arguments as you mentioned
    result_bytes, message = process_file(mock_file, target_filename) 

    if not result_bytes:
         raise HTTPException(status_code=500, detail=message)
    
    target_filename_stripped = target_filename.split(".")[0]
    output_filename = f"secure_{target_filename_stripped}.pdf"
    
    output_path = os.path.join(LOCAL_OUTPUT_DIRECTORY, output_filename)
    
    with open(output_path, 'wb') as out_f:
        out_f.write(result_bytes)

    target_email = payload.target_email

    email_success = send_smtp_email(target_email, output_path, output_filename)
    if email_success:
        print("Workflow Complete.")
    
    os.remove(output_path)
    
    return {
        "status": "success", 
        "message": message, 
        "saved_to": output_path
    }






# app_password_google = "glng qeoj weak xlbk"
