from flask import Flask, render_template, jsonify, send_from_directory, request
import threading
import cv2
import os
import numpy as np
import datetime
import time

app = Flask(__name__)

# Globals for recognition control
recognition_active = False
recognition_thread = None
stop_event = threading.Event()

# Initialize face recognition variables
authorized_faces_folder = r"C:\Users\hp\Downloads\project\Untitled Folder 3\authorized_faces"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
CONFIDENCE_THRESHOLD = 100

unauthorized_folder = os.path.join(os.getcwd(), "unauthorized_snapshots")
os.makedirs(unauthorized_folder, exist_ok=True)

# Load authorized faces
def get_label_name_map(folder):
    label_name_map = {}
    for idx, person_name in enumerate(os.listdir(folder)):
        person_path = os.path.join(folder, person_name)
        if os.path.isdir(person_path):
            label_name_map[idx] = person_name
    return label_name_map

label_name_map = get_label_name_map(authorized_faces_folder)

def load_authorized_faces(folder):
    images = []
    labels = []
    label = 0
    for person_name in os.listdir(folder):
        person_folder = os.path.join(folder, person_name)
        if not os.path.isdir(person_folder):
            continue
        for file in os.listdir(person_folder):
            if file.lower().endswith((".jpg", ".png")):
                image_path = os.path.join(person_folder, file)
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Warning: Could not read image {image_path}")
                    continue
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                for (x, y, w, h) in faces:
                    face = gray[y:y + h, x:x + w]
                    images.append(face)
                    labels.append(label)
        label += 1
    return images, labels

faces, labels = load_authorized_faces(authorized_faces_folder)
if len(faces) == 0:
    raise RuntimeError("No authorized faces found!")

recognizer.train(faces, np.array(labels))

# Dummy email sender placeholder
def send_email_with_attachment(file_path):
    print(f"Sending email alert with attachment: {file_path}")

email_cooldown = {}
COOLDOWN_PERIOD = 300  # 5 minutes

def send_email_threaded_with_cooldown(image_path):
    current_time = time.time()
    key = os.path.basename(image_path)
    last_sent_time = email_cooldown.get(key, 0)
    if current_time - last_sent_time > COOLDOWN_PERIOD:
        email_cooldown[key] = current_time
        thread = threading.Thread(target=send_email_with_attachment, args=(image_path,))
        thread.daemon = True
        thread.start()
    else:
        print(f"Email cooldown active for {key}, skipping send.")

def recognition_function(stop_event):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_in_frame = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces_in_frame:
            detected_face = gray_frame[y:y + h, x:x + w]
            try:
                label, confidence = recognizer.predict(detected_face)
            except Exception as e:
                print(f"Recognition error: {e}")
                continue

            if confidence < CONFIDENCE_THRESHOLD:
                user_name = label_name_map.get(label, f"User {label}")
                cv2.putText(frame, f"{user_name} - {round(100 - confidence)}%", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unauthorized", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                face_img = frame[y:y + h, x:x + w]
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(unauthorized_folder, f"unauth_{timestamp}.jpg")
                cv2.imwrite(file_path, face_img)

                send_email_threaded_with_cooldown(file_path)

        # Optional: remove this if running headless or without GUI
        # Use try-except to avoid crashes if window is closed manually
        try:
            cv2.imshow("Real-Time Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
        except cv2.error:
            # If window is closed or error happens, stop recognition
            stop_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    global recognition_active, recognition_thread, stop_event
    if recognition_active:
        return jsonify({"status": "already running"})

    stop_event.clear()
    recognition_thread = threading.Thread(target=recognition_function, args=(stop_event,))
    recognition_thread.daemon = True
    recognition_thread.start()
    recognition_active = True
    return jsonify({"status": "started"})

@app.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    global recognition_active, stop_event
    if not recognition_active:
        return jsonify({"status": "not running"})

    stop_event.set()
    recognition_active = False
    return jsonify({"status": "stopped"})

@app.route('/unauthorized_logs', methods=['GET'])
def unauthorized_logs():
    snaps = os.listdir(unauthorized_folder)
    snaps = [snap for snap in snaps if snap.lower().endswith((".jpg", ".png"))]
    return jsonify({"snapshots": snaps})

@app.route('/unauthorized_snapshots/<filename>')
def serve_unauthorized_snapshots(filename):
    return send_from_directory(unauthorized_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
