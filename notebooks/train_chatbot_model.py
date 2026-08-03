"""
Module B3 — Chatbot
Hybrid: TF-IDF + Logistic Regression intent classifier trained on intents.json,
with rule-based FAQ response lookup. Falls back to a default reply below a
confidence threshold (handled in chatbot_service.py at inference time).
"""
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

INTENTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "intents.json")

if __name__ == "__main__":
    with open(INTENTS_PATH) as f:
        intents = json.load(f)["intents"]

    X, y = [], []
    responses = {}
    for intent in intents:
        responses[intent["tag"]] = intent["response"]
        for pattern in intent["patterns"]:
            X.append(pattern.lower())
            y.append(intent["tag"])

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_vec, y)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
    joblib.dump(
        {"model": clf, "vectorizer": vectorizer, "responses": responses},
        os.path.join(out_dir, "chatbot_model.pkl"),
    )
    print(f"Trained chatbot on {len(X)} patterns across {len(responses)} intents")
    print("Saved chatbot_model.pkl")
