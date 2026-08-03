"""
Module C1 — Unified Pipeline
Importing this module (once, at FastAPI startup) triggers each service module
to load its models exactly once (see the module-level joblib.load / cv2.read
calls in cv_service.py, nlp_service.py, chatbot_service.py). Routers then call
the functions below instead of touching models directly.
"""
from app.services import cv_service, nlp_service, chatbot_service

import time

# --- tiny in-memory stats store for GET /dashboard/stats ---
_stats = {
    "visits": [],       # list of {customer_id/status, timestamp}
    "sentiments": [],   # list of {sentiment, timestamp}
}


def recognize_face(image_bytes: bytes) -> dict:
    result = cv_service.recognize_face(image_bytes)
    _stats["visits"].append({"result": result, "ts": time.time()})
    return result


def classify_product(image_bytes: bytes) -> dict:
    return cv_service.classify_product(image_bytes)


def analyze_sentiment(text: str) -> dict:
    result = nlp_service.analyze_sentiment(text)
    _stats["sentiments"].append({"sentiment": result["sentiment"], "ts": time.time()})
    return result


def chatbot_reply(message: str) -> dict:
    return chatbot_service.get_reply(message)


def get_dashboard_stats() -> dict:
    total_visits = len(_stats["visits"])
    returning = sum(1 for v in _stats["visits"] if v["result"].get("status") == "returning_customer")
    sentiment_counts = {}
    for s in _stats["sentiments"]:
        sentiment_counts[s["sentiment"]] = sentiment_counts.get(s["sentiment"], 0) + 1

    return {
        "total_visits": total_visits,
        "returning_customers": returning,
        "unique_visitors_seen": total_visits - returning,
        "sentiment_breakdown": sentiment_counts,
        "total_feedback_analyzed": len(_stats["sentiments"]),
    }
