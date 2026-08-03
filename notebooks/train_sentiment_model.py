"""
Module B2 — Sentiment Analysis (REAL DATA VERSION)
Uses the IMDB 50K Movie Reviews dataset (data/movie_reviews.csv), a real,
human-labeled binary (positive/negative) sentiment dataset with 50,000 rows.

Domain note (mention this in your report): this is movie-review text, not
retail/product-review text. Sentiment words (amazing/terrible/love/hate)
transfer reasonably well across domains, but retail-specific phrasing
("fast shipping", "true to size") won't be as sharp as it would be with a
genuine e-commerce review dataset. Documented tradeoff given time
constraints, not an oversight.
"""
import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "movie_reviews.csv")


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"<br\s*/?>", " ", text)   # strip HTML line breaks present in this dataset
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["review", "sentiment"])
    df["clean_text"] = df["review"].apply(clean_text)
    print(f"Loaded {len(df)} real labeled reviews from {DATA_PATH}")
    print(df["sentiment"].value_counts().to_string())
    return df


if __name__ == "__main__":
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"], df["sentiment"], test_size=0.2, random_state=42, stratify=df["sentiment"]
    )

    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X_train_vec, y_train)

    preds = clf.predict(X_test_vec)
    print(f"Test accuracy: {accuracy_score(y_test, preds):.3f}")
    print(classification_report(y_test, preds))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
    joblib.dump(clf, os.path.join(out_dir, "sentiment_model.pkl"))
    joblib.dump(vectorizer, os.path.join(out_dir, "vectorizer.pkl"))
    print("Saved sentiment_model.pkl + vectorizer.pkl (trained on real IMDB data)")