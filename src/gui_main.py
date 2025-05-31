import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import time
import threading
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging

# === Paths ===
project_dir = r"C:\Users\hp\Downloads\project\Untitled Folder 3"
model_path = os.path.join(project_dir, "models", "face_trained.yml")
authorized_dir = os.path.join(project_dir, "authorized_faces")
log_file_path = os.path.join(project_dir, "logs", "unauthorized.log")

# === Logging ===
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(fh)

# === Email Config ===
sender_email = "aayampawar@gmail.com"
receiver_email = "pawaraayam@gmail.com"
password = "dhsetsskrgpcwbcv"

def send_email(subject, body, image_path):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with open(image_path, "rb") as f:
            img_data = f.read()
            msg.attach(MIMEImage(img_data, name=os.path.basename(image_path)))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        logger.info("✅ Email sent.")
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")

# === Load face recognizer ===
recognizer = cv2.face.LBPHFaceRecognizer_create()
if os.path.exists(model_path):
    recognizer.read(model_path)
else:
    logger.error("❌ Model file not found.")
    exit()

# === Load label map ===
label_map = {idx: name for idx, name in enumerate(os.listdir(authorized_dir))}
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === GUI Class ===
class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Real-Time Face Recognition System")
        self.root.geometry("800x600")
        self.running = True

        self.video_label = tk.Label(self.root)
        self.video_label.pack(padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("🟢 System Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_var.set("❌ Could not access webcam")
            logger.error("Webcam not available.")
            return

        self.last_email_time = 0
        self.cooldown = 60  # seconds

        self.update_frame()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("❌ Failed to grab frame")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            id_, confidence = recognizer.predict(face_roi)

            if confidence < 60:
                label = f"Authorized: {label_map.get(id_, 'Unknown')}"
                color = (0, 255, 0)
            elif confidence < 85:
                label = "Partially Authorized"
                color = (0, 255, 255)
            else:
                label = "❌ Unauthorized"
                color = (0, 0, 255)

                now = time.time()
                if now - self.last_email_time > self.cooldown:
                    self.last_email_time = now
                    snapshot_path = os.path.join(project_dir, "logs", f"unauthorized_{int(now)}.jpg")
                    cv2.imwrite(snapshot_path, frame)
                    logger.warning(f"🚨 Unauthorized face detected. Snapshot saved at: {snapshot_path}")
                    threading.Thread(
                        target=send_email,
                        args=("🚨 Alert: Unauthorized Face Detected", "See the attached image.", snapshot_path),
                        daemon=True
                    ).start()

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            self.status_var.set(label)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def close(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()

# === Main Launch ===
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
