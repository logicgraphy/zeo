import bcrypt
import random
import string
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email: str, code: str) -> bool:
    """Send verification email (mock implementation)"""
    # In production, use a real email service like SendGrid, AWS SES, etc.
    # For demo purposes, we'll just print the code
    print(f"🔐 Verification code for {email}: {code}")
    print(f"📧 Email would be sent to: {email}")
    
    # Uncomment and configure for real email sending:
    # try:
    #     smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    #     smtp_port = int(os.getenv("SMTP_PORT", "587"))
    #     smtp_username = os.getenv("SMTP_USERNAME")
    #     smtp_password = os.getenv("SMTP_PASSWORD")
    #     
    #     msg = MIMEMultipart()
    #     msg['From'] = smtp_username
    #     msg['To'] = email
    #     msg['Subject'] = "Email Verification - SG AI"
    #     
    #     body = f"Your verification code is: {code}"
    #     msg.attach(MIMEText(body, 'plain'))
    #     
    #     server = smtplib.SMTP(smtp_server, smtp_port)
    #     server.starttls()
    #     server.login(smtp_username, smtp_password)
    #     server.send_message(msg)
    #     server.quit()
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
    #     return False
    
    return True  # Mock success 