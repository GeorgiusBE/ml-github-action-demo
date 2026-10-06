"""Load the saved model and make one example prediction."""

from pathlib import Path

import joblib
from sklearn.datasets import load_breast_cancer

MODEL_PATH = Path("artifacts/model.joblib")


def main() -> None:
    if not MODEL_PATH.exists():
        raise SystemExit("Model not found. Run: python src/train.py")

    model = joblib.load(MODEL_PATH)
    dataset = load_breast_cancer()

    example = dataset.data[[0]]
    prediction = int(model.predict(example)[0])
    probability = float(model.predict_proba(example)[0, prediction])
    label = dataset.target_names[prediction]

    print(f"Prediction: {label}")
    print(f"Probability for predicted class: {probability:.4f}")


if __name__ == "__main__":
    main()
