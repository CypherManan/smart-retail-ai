"""
Module A2 — Product Image Classifier
Speedrun choice: color-histogram + HOG features -> SVM instead of MobileNetV2.
Why: no TensorFlow download/training time needed, trains in seconds, still a
real, defensible ML pipeline (feature extraction + classical classifier).
If you have spare time later, swap in MobileNetV2 transfer learning —
the pipeline.py interface stays identical either way.
"""
import os
import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

CATEGORIES = ["shoes", "bags", "electronics", "clothing", "groceries"]
IMG_SIZE = 64
N_PER_CLASS = 120  # synthetic demo dataset if no real images are supplied

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "products")


def extract_features(img):
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hog = cv2.HOGDescriptor((64, 64), (16, 16), (8, 8), (8, 8), 9)
    hog_feat = hog.compute(gray).flatten()
    return np.concatenate([hist, hog_feat])


def make_synthetic_dataset():
    """Generates class-separable synthetic 'product photos' so the pipeline
    is fully runnable today without waiting on a real image scrape/download.
    Replace this with real images in data/products/<class>/*.jpg any time —
    train_from_real_images() below will pick them up automatically."""
    rng = np.random.RandomState(42)
    X, y = [], []
    base_colors = {
        "shoes": (120, 80, 60),
        "bags": (60, 100, 140),
        "electronics": (30, 30, 30),
        "clothing": (180, 60, 120),
        "groceries": (60, 160, 60),
    }
    for label, color in base_colors.items():
        for _ in range(N_PER_CLASS):
            img = np.ones((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
            noise = rng.randint(-25, 25, (IMG_SIZE, IMG_SIZE, 3))
            img[:, :] = color
            img = np.clip(img.astype(int) + noise, 0, 255).astype(np.uint8)
            cv2.rectangle(img, (10, 10), (54, 54), tuple(int(c * 0.7) for c in color), 2)
            X.append(extract_features(img))
            y.append(label)
    return np.array(X), np.array(y)


def train_from_real_images():
    X, y = [], []
    for label in CATEGORIES:
        folder = os.path.join(DATA_DIR, label)
        if not os.path.isdir(folder):
            return None
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            img = cv2.imread(path)
            if img is None:
                continue
            X.append(extract_features(img))
            y.append(label)
    if not X:
        return None
    return np.array(X), np.array(y)


if __name__ == "__main__":
    real = train_from_real_images()
    if real is not None:
        X, y = real
        print(f"Training on {len(X)} real images from data/products/")
    else:
        X, y = make_synthetic_dataset()
        print(f"No data/products/<class>/ images found — training on {len(X)} synthetic samples")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = SVC(kernel="rbf", probability=True, C=10)
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    print(f"Test accuracy: {acc:.3f}")

    out_path = os.path.join(os.path.dirname(__file__), "..", "app", "models", "product_classifier.pkl")
    joblib.dump({"model": clf, "categories": CATEGORIES}, out_path)
    print(f"Saved -> {out_path}")
