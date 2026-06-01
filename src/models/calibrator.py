import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import LabelBinarizer


class ProbabilityCalibrator:
    def __init__(self):
        self.calibrators: list = []

    def fit(self, predicted_probs: np.ndarray, y_true: np.ndarray):
        n_classes = predicted_probs.shape[1]
        y_bin = LabelBinarizer().fit_transform(y_true)
        self.calibrators = []
        for i in range(n_classes):
            iso_reg = IsotonicRegression(out_of_bounds="clip")
            iso_reg.fit(predicted_probs[:, i], y_bin[:, i])
            self.calibrators.append(iso_reg)

    def calibrate(self, predicted_probs: np.ndarray) -> np.ndarray:
        calibrated = np.column_stack([
            cal.predict(predicted_probs[:, i])
            for i, cal in enumerate(self.calibrators)
        ])
        row_sums = calibrated.sum(axis=1, keepdims=True)
        return calibrated / row_sums
