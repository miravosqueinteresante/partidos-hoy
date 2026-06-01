import json
import pandas as pd
import numpy as np
from src.features.build_features import FeatureBuilder
from src.models.trainer import ModelTrainer, FEATURE_COLS
from src.models.calibrator import ProbabilityCalibrator
from src.models.predictor import PredictionGenerator


def test_end_to_end_pipeline():
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        "home_team": [f"Team_{np.random.randint(1, 21)}" for _ in range(n)],
        "away_team": [f"Team_{np.random.randint(1, 21)}" for _ in range(n)],
        "home_goals": np.random.poisson(1.5, n),
        "away_goals": np.random.poisson(1.2, n),
        "date": pd.date_range("2025-01-01", periods=n, freq="7D"),
    })
    df["league"] = "Test League"

    builder = FeatureBuilder()
    featured = builder.build(df)
    featured = featured.dropna()

    trainer = ModelTrainer()
    trainer.train(featured, target_col="home_win")

    upcoming = featured.tail(3).copy()
    generator = PredictionGenerator()
    generator.trainer = trainer

    X_upcoming = upcoming[[c for c in FEATURE_COLS if c in upcoming.columns]]
    X_upcoming = X_upcoming.reindex(columns=FEATURE_COLS, fill_value=0)
    raw_probs = trainer.predict_proba(X_upcoming)
    calibrator = ProbabilityCalibrator()
    calibrator.fit(raw_probs, upcoming["home_win"].values[:len(raw_probs)])
    generator.calibrator = calibrator

    upcoming["league"] = "Test League"
    upcoming["date"] = upcoming["date"].astype(str)
    json_output = generator.generate(upcoming)
    parsed = json.loads(json_output)
    assert "matches" in parsed
    assert len(parsed["matches"]) == 3
    for m in parsed["matches"]:
        probs = m["probabilities"]
        assert abs(sum(probs.values()) - 1.0) < 0.01
        assert "api_prediction" in m
