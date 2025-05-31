import cv2
import os
import numpy as np
import datetime
import threading

class FaceRecognitionRunner:
    def __init__(self, authorized_faces_folder, unauthorized_folder):
        self.authorized_faces_folder = authorized_faces_folder
        self.unauthorized_folder = unauthorized_folder
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.confidence_threshold = 100
        self.label_name_map = self._get_label_name_map()
        self.running = False
        self.thread = None

        # Load and train on authorized faces
        print("📂 Loading authorized faces...")
        faces, labels = self._load_authorized_faces()
        if len(faces) == 0:
            raise RuntimeError("❌ No authorized faces found! Please add authorized faces in folders.")
        self.recognizer.train(faces, np.array(labels))

        # Create unauthorized folder if not exists
        if not os.path.exists(self.unauthorized_folder):
            os.makedirs(self.unauthorized_folder)

    def _get_label_name_map(self):
        label_name_map = {}
        for idx, person_name in enumerate(os.listdir(self.authorized_faces_folder)):
            person_path = os.path.join(self.authorized_faces_folder, person_name)
            if os.path.isdir(person_path):
                label_name_map[idx] = person_name
        return label_name_map

    def _load_authorized_faces(self):
        images = []
        labels = []
        label = 0
        for person_name in os.listdir(self.authorized_faces_folder):
            person_folder = os.path.join(self.authorized_faces_folder, person_name)
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
                    faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                    for (x, y, w, h) in faces:
                        face = gray[y:y + h, x:x + w]
                        images.append(face)
                        labels.append(label)
            label += 1
        return images, labels

    def start(self):
        if self.running:
            print("Recognition already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_recognition_loop, daemon=True)
        self.thread.start()
        print("Recognition started.")

    def stop(self):
        if not self.running:
            print("Recognition is not running.")
            return
        self.running = False
        if self.thread:
            self.thread.join()
        print("Recognition stopped.")

    def _run_recognition_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open webcam.")
            self.running = False
            return

        print("📸 Press 'q' in the webcam window to quit recognition manually.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces_in_frame = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces_in_frame:
                detected_face = gray_frame[y:y + h, x:x + w]
                try:
                    label, confidence = self.recognizer.predict(detected_face)
                except Exception as e:
                    print(f"Recognition error: {e}")
                    continue

                if confidence < self.confidence_threshold:
                    user_name = self.label_name_map.get(label, f"User {label}")
                    cv2.putText(frame, f"{user_name} - {round(100 - confidence)}%", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    # Unauthorized face detected - save snapshot
                    cv2.putText(frame, "Unauthorized", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    face_img = frame[y:y + h, x:x + w]
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = os.path.join(self.unauthorized_folder, f"unauth_{timestamp}.jpg")
                    cv2.imwrite(file_path, face_img)

            cv2.imshow("Real-Time Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        cap.release()
        cv2.destroyAllWindows()
