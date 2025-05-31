import cv2
from flask import Response

class Camera:
    def __init__(self, face_detector):
        # Initialize webcam capture
        self.cap = cv2.VideoCapture(0)
        self.face_detector = face_detector  # Your face detection model/function

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Convert frame to grayscale for face detection (if needed)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces - assuming face_detector returns list of rectangles
        faces = self.face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)

        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return None
        
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
