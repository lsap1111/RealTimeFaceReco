import os
import cv2
import numpy as np

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(BASE_DIR, "../dataset")
model_path = os.path.join(BASE_DIR, "../models/authorized_face_recognizer.yml")

# Create recognizer and face detector
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

faces = []
labels = []

# Iterate through dataset folder
for person_id in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_id)
    if not os.path.isdir(person_folder):
        continue
    for img_name in os.listdir(person_folder):
        img_path = os.path.join(person_folder, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        detected = face_cascade.detectMultiScale(img, 1.1, 5)
        for (x, y, w, h) in detected:
            faces.append(img[y:y+h, x:x+w])
            labels.append(int(person_id))

# Train and save model
recognizer.train(faces, np.array(labels))
recognizer.save(model_path)
print(f"✅ Model trained and saved to {model_path}")
