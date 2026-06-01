import numpy as np
from src.models.calibrator import ProbabilityCalibrator


def test_calibrator_improves_brier():
    np.random.seed(42)
    n = 500
    true_probs = np.random.dirichlet([1, 1, 1], n)
    predicted = true_probs + np.random.normal(0, 0.1, true_probs.shape)
    predicted = np.clip(predicted, 0.01, 0.99)
    predicted = predicted / predicted.sum(axis=1, keepdims=True)

    y_true = np.argmax(true_probs, axis=1)

    calibrator = ProbabilityCalibrator()
    calibrator.fit(predicted, y_true)
    calibrated = calibrator.calibrate(predicted)

    brier_before = np.mean((predicted - np.eye(3)[y_true]) ** 2)
    brier_after = np.mean((calibrated - np.eye(3)[y_true]) ** 2)
    assert brier_after <= brier_before + 0.01


def test_calibrated_probs_sum_to_one():
    np.random.seed(42)
    probs = np.random.dirichlet([1, 1, 1], 10)
    calibrator = ProbabilityCalibrator()
    calibrator.fit(probs, np.random.randint(0, 3, 10))
    calibrated = calibrator.calibrate(probs)
    np.testing.assert_almost_equal(calibrated.sum(axis=1), [1.0] * 10)
