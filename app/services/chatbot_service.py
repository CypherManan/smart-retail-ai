import os
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

_bundle = joblib.load(os.path.join(MODELS_DIR, "chatbot_model.pkl"))
_model = _bundle["model"]
_vectorizer = _bundle["vectorizer"]
_responses = _bundle["responses"]

CONFIDENCE_THRESHOLD = 0.35
DEFAULT_REPLY = "I'm not fully sure about that yet — could you rephrase, or ask about orders, returns, store hours, or payments?"


def get_reply(message: str) -> dict:
    vec = _vectorizer.transform([message.lower()])
    proba = _model.predict_proba(vec)[0]
    idx = proba.argmax()
    confidence = float(proba[idx])
    intent = _model.classes_[idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return {"reply": DEFAULT_REPLY, "intent": "fallback", "confidence": round(confidence, 4)}

    return {"reply": _responses[intent], "intent": intent, "confidence": round(confidence, 4)}
