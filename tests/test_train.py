"""Small tests that run quickly enough for CI."""

from src.train import build_model, load_data, train_and_evaluate


def test_data_is_binary_classification_problem():
    X, y = load_data()

    assert X.shape[0] == len(y)
    assert X.shape[1] > 1
    assert set(y) == {0, 1}


def test_model_pipeline_has_preprocessing_and_classifier():
    model = build_model()

    assert "scaler" in model.named_steps
    assert "classifier" in model.named_steps


def test_training_produces_good_accuracy():
    _, metrics = train_and_evaluate()

    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert metrics["accuracy"] >= 0.95
