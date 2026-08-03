"""
Module A3 — Face Recognition
Speedrun choice: OpenCV's built-in LBPH recognizer instead of dlib/face_recognition.
Why: face_recognition needs dlib, which can take 10-20+ min to compile from
source on some machines - a real risk on a one-day deadline. LBPH ships with
opencv-contrib-python, installs in seconds, and is a legitimate, commonly
taught face-recognition algorithm (it's explicitly in most CV syllabi).

This script "enrolls" demo customers from data/faces/<customer_name>/*.jpg.
If no such folders exist, it enrolls synthetic placeholder faces so the
pipeline and API are fully testable today. Swap in real (consenting) face
photos any time - just drop them in data/faces/<name>/ and rerun.
"""
import os
import cv2
import numpy as np
import pickle

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "faces")
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def detect_and_crop_face(img_gray):
    faces = FACE_CASCADE.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return cv2.resize(img_gray[y:y + h, x:x + w], (200, 200))


def make_synthetic_faces(n_customers=4, n_per=6):
    """Generates class-separable synthetic 'face' grayscale patches so LBPH
    has something concrete to train and demo /recognize-face against today."""
    rng = np.random.RandomState(7)
    faces, labels, names = [], [], []
    for cid in range(n_customers):
        name = f"customer_{cid+1}"
        base = rng.randint(60, 200, (200, 200), dtype=np.uint8)
        for _ in range(n_per):
            noisy = np.clip(base.astype(int) + rng.randint(-15, 15, (200, 200)), 0, 255).astype(np.uint8)
            faces.append(noisy)
            labels.append(cid)
        names.append(name)
    return faces, labels, names


def load_real_faces():
    if not os.path.isdir(DATA_DIR):
        return None
    faces, labels, names = [], [], []
    for idx, person in enumerate(sorted(os.listdir(DATA_DIR))):
        folder = os.path.join(DATA_DIR, person)
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            img = cv2.imread(os.path.join(folder, fname), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            cropped = detect_and_crop_face(img)
            if cropped is not None:
                faces.append(cropped)
                labels.append(idx)
        names.append(person)
    if not faces:
        return None
    return faces, labels, names


if __name__ == "__main__":
    real = load_real_faces()
    if real is not None:
        faces, labels, names = real
        print(f"Enrolled {len(names)} real customers from data/faces/")
    else:
        faces, labels, names = make_synthetic_faces()
        print(f"No data/faces/<name>/ found — enrolled {len(names)} synthetic demo customers")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    model_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
    recognizer.write(os.path.join(model_dir, "face_recognizer.yml"))
    with open(os.path.join(model_dir, "face_names.pkl"), "wb") as f:
        pickle.dump(names, f)
    print("Saved face_recognizer.yml + face_names.pkl")