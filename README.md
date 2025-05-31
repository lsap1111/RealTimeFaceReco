# Real-Time Face Recognition System 👁️🧠
A robust, real-time face recognition and monitoring system built with Python, OpenCV, and Flask. Detects and verifies faces from webcam input, logs unauthorized access attempts with snapshot capture, and sends email alerts to the administrator. Includes a responsive web interface with live video feed, login authentication, snapshot gallery, and dark mode.

# 🔧 Features
•	🎥 Real-time face detection and recognition via webcam
•	🔐 Admin login for secure access to dashboard
•	📷 Snapshot capture of unauthorized faces
•	✉️ Email alerts with image attachment using SMTP
•	📊 Live face count and recognition confidence
•	🌙 Dark/Light mode toggle
•	💾 Organized file structure for scalability
•	🧠 Supports DeepFace (optional) for high-accuracy recognition

# 📁 Project Structure
project/
├── static/
│   ├── css/style.css
│   ├── js/dashboard.js
│   └── snapshots/              # Captured images of unknown faces
├── templates/
│   ├── layout.html             # Base HTML structure
│   ├── login.html              # Admin login page
│   └── dashboard.html          # Main dashboard with live feed
├── app.py                      # Flask app entry point
├── auth.py                     # Login session management
├── camera.py                   # Webcam stream logic
├── face_recognition.py         # Face detection/recognition logic
├── models/                     # Trained face models
├── logs/                       # Application logs
├── dataset/                    # Training images
├── authorized_faces/           # Known face images
└── src/
    ├── app/
    ├── trainer/
    └── email_utils/

# 📦 Requirements
Install the necessary packages:
pip install -r requirements.txt
Key Libraries:
•	OpenCV
•	Flask
•	DeepFace *(optional)*
•	NumPy
•	smtplib (built-in)
•	threading
 
 # 🚀 How to Run
1.	Clone the repo:
    git clone https://github.com/yourusername/face-recognition-webapp.git
    cd face-recognition-webapp
2.	Set up your face dataset in the `authorized_faces/` directory.
3.	Train the face model:
    python src/trainer/train_model.py
4.	Start the Flask server:
    python app.py
5.	Open the browser and visit:
    http://localhost:5000

# 🔐 Admin Login
Default credentials (change in auth.py):
Username: admin
Password: admin123

# 📬 Email Alerts Configuration
Edit the SMTP settings in src/email_utils/email_sender.py:

EMAIL_ADDRESS = "youremail@example.com"
EMAIL_PASSWORD = "yourpassword"
TO_ADDRESS = "destination@example.com"


# 📸 Add New Faces
6.	Add a new folder with the person's name under `authorized_faces/`.
7.	Add multiple clear images of their face.
8.	Re-run the training script.
🧪 Testing
Tested on:
Windows/Linux
Python 3.8+
Webcam-enabled devices

# 📜 License
This project is open source and available under the MIT License.

# ❤️ Contributions
Feel free to fork, submit pull requests, or suggest features. Contributions are welcome!

# ✨ Acknowledgments
•	OpenCV - https://opencv.org/
•	DeepFace - https://github.com/serengil/deepface
•	Flask, NumPy, and the Python open-source community.
