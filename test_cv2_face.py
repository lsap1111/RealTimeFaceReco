import cv2

print("cv2 version:", cv2.__version__)

if hasattr(cv2, 'face'):
    print("cv2.face is available")
    if hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
        print("LBPHFaceRecognizer_create is available ✅")
    else:
        print("LBPHFaceRecognizer_create is NOT available ❌")
else:
    print("cv2.face is NOT available ❌")
