"""Train a small binary-classification model and save model + metrics artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MY_NAME = "Georgius"

RANDOM_STATE = 42
ARTIFACT_DIR = Path("artifacts")
MODEL_PATH = ARTIFACT_DIR / "model.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"


def load_data():
    """Load a small dataset bundled with scikit-learn (no network needed)."""
    dataset = load_breast_cancer()
    return dataset.data, dataset.target


def build_model() -> Pipeline:
    """Create a reproducible preprocessing + model pipeline."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
            ),
        ]
    )


def train_and_evaluate() -> tuple[Pipeline, dict[str, float]]:
    """Split the data, train the model, and return evaluation metrics."""
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = build_model()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions)),
        "recall": float(recall_score(y_test, predictions)),
        "f1": float(f1_score(y_test, predictions)),
    }
    return model, metrics


def save_artifacts(model: Pipeline, metrics: dict[str, float]) -> None:
    """Save outputs that a later CI/CD stage could publish or deploy."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    model, metrics = train_and_evaluate()
    save_artifacts(model, metrics)

    print("Training complete")
    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
