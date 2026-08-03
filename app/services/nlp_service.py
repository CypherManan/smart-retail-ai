import os
import re
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

_sentiment_model = joblib.load(os.path.join(MODELS_DIR, "sentiment_model.pkl"))
_vectorizer = joblib.load(os.path.join(MODELS_DIR, "vectorizer.pkl"))


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_sentiment(text: str) -> dict:
    cleaned = clean_text(text)
    vec = _vectorizer.transform([cleaned])
    proba = _sentiment_model.predict_proba(vec)[0]
    classes = _sentiment_model.classes_
    idx = proba.argmax()
    return {
        "sentiment": classes[idx],
        "confidence": round(float(proba[idx]), 4),
        "scores": {cls: round(float(p), 4) for cls, p in zip(classes, proba)},
    }
