import threading
import cv2
import datetime
import os
import time

class FaceRecognizerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.running = False
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Could not open webcam.")
            return
        self.running = True

        while not self._stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Your recognition logic here
            # For example: detect faces, recognize, save unauthorized snapshots
            # (You can import your existing recognition code here or write a method)

            cv2.imshow("Recognition Running", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.running = False

    def stop(self):
        self._stop_event.set()
