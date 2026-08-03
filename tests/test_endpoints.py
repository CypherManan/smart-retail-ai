import io
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "demo-key-123"}


def _make_image_bytes(color=(120, 80, 60)):
    img = np.ones((200, 200, 3), dtype=np.uint8)
    img[:, :] = color
    _, buf = cv2.imencode(".jpg", img)
    return io.BytesIO(buf.tobytes())


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200


def test_missing_api_key_rejected():
    resp = client.post("/chatbot", json={"message": "hi"})
    assert resp.status_code == 401


def test_wrong_api_key_rejected():
    resp = client.post("/chatbot", json={"message": "hi"}, headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_sentiment_positive():
    resp = client.post(
        "/analyze-sentiment",
        json={"text": "I love this so much, best purchase ever"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["sentiment"] == "positive"
    assert 0 <= body["confidence"] <= 1


def test_sentiment_negative():
    resp = client.post(
        "/analyze-sentiment",
        json={"text": "This is absolutely terrible, it broke immediately"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["sentiment"] == "negative"


def test_chatbot_known_intent():
    resp = client.post("/chatbot", json={"message": "where is my order"}, headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["intent"] == "order_status"


def test_chatbot_fallback():
    resp = client.post("/chatbot", json={"message": "asdkjaskdj gibberish text"}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["intent"] == "fallback"


def test_classify_product():
    img_bytes = _make_image_bytes()
    resp = client.post(
        "/classify-product",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] in ["shoes", "bags", "electronics", "clothing", "groceries"]


def test_recognize_face_no_face():
    rng = np.random.RandomState(0)
    noise = rng.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", noise)
    resp = client.post(
        "/recognize-face",
        files={"file": ("noface.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "no_face_detected"


def test_dashboard_stats():
    resp = client.get("/dashboard/stats", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "total_visits" in body
    assert "sentiment_breakdown" in body
