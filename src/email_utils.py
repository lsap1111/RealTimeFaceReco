# src/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging
import os

# Email configuration
SENDER_EMAIL = "aayampawar@gmail.com"
SENDER_PASSWORD = "dhsetsskrgpcwbcv"  # Be sure to keep this secure!
RECIPIENT_EMAIL = "pawaraayam@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def setup_logger(log_file="logs/app.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger("FaceRecognitionApp")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

logger = setup_logger()

def send_email_with_attachment(image_path):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "Unauthorized Access Detected"

    msg.attach(MIMEText("An unauthorized person was detected. See the attached image.", 'plain'))

    try:
        with open(image_path, 'rb') as f:
            img = MIMEImage(f.read())
            msg.attach(img)
    except Exception as e:
        logger.error(f"Failed to attach image: {e}")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logger.info("✅ Email sent successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
