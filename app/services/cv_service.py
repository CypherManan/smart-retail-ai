import os
import pickle
import numpy as np
import cv2
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# --- load once at import time (module is imported once by pipeline.py) ---
_product_bundle = joblib.load(os.path.join(MODELS_DIR, "product_classifier.pkl"))
_product_model = _product_bundle["model"]
_categories = _product_bundle["categories"]

_face_recognizer = cv2.face.LBPHFaceRecognizer_create()
_face_recognizer.read(os.path.join(MODELS_DIR, "face_recognizer.yml"))
with open(os.path.join(MODELS_DIR, "face_names.pkl"), "rb") as f:
    _face_names = pickle.load(f)

CONFIDENCE_THRESHOLD = 80.0  # LBPH: LOWER distance = better match; above this -> "unknown"


def _bytes_to_cv2_image(image_bytes: bytes):
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _extract_product_features(img):
    img = cv2.resize(img, (64, 64))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hog = cv2.HOGDescriptor((64, 64), (16, 16), (8, 8), (8, 8), 9)
    hog_feat = hog.compute(gray).flatten()
    return np.concatenate([hist, hog_feat]).reshape(1, -1)


def classify_product(image_bytes: bytes) -> dict:
    img = _bytes_to_cv2_image(image_bytes)
    if img is None:
        return {"error": "Could not decode image"}
    features = _extract_product_features(img)
    probs = _product_model.predict_proba(features)[0]
    idx = int(np.argmax(probs))
    return {"category": _categories[idx], "confidence": round(float(probs[idx]), 4)}


def recognize_face(image_bytes: bytes) -> dict:
    img = _bytes_to_cv2_image(image_bytes)
    if img is None:
        return {"error": "Could not decode image"}
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return {"status": "no_face_detected"}

    x, y, w, h = faces[0]
    face_crop = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
    label_idx, distance = _face_recognizer.predict(face_crop)

    if distance > CONFIDENCE_THRESHOLD:
        return {"status": "unknown_customer", "distance": round(float(distance), 2)}

    return {
        "status": "returning_customer",
        "customer_id": _face_names[label_idx],
        "distance": round(float(distance), 2),
    }
