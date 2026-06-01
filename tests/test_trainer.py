import pandas as pd
import numpy as np
from src.models.trainer import ModelTrainer


def test_trainer_creates_model():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "elo_diff": np.random.randn(n),
        "home_elo": np.random.randn(n) * 100 + 1500,
        "away_elo": np.random.randn(n) * 100 + 1500,
        "home_form_rolling_5": np.random.rand(n),
        "away_form_rolling_5": np.random.rand(n),
        "home_goals_rolling_5": np.random.rand(n) * 2,
        "home_conceded_rolling_5": np.random.rand(n),
        "away_goals_rolling_5": np.random.rand(n) * 2,
        "away_conceded_rolling_5": np.random.rand(n),
        "home_win": np.random.choice([0.0, 1.0, 2.0], n),
    })
    trainer = ModelTrainer()
    trainer.train(df, target_col="home_win")
    assert trainer.model is not None


def test_predict_returns_probabilities():
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "elo_diff": np.random.randn(n),
        "home_elo": np.random.randn(n) * 100 + 1500,
        "away_elo": np.random.randn(n) * 100 + 1500,
        "home_form_rolling_5": np.random.rand(n),
        "away_form_rolling_5": np.random.rand(n),
        "home_goals_rolling_5": np.random.rand(n) * 2,
        "home_conceded_rolling_5": np.random.rand(n),
        "away_goals_rolling_5": np.random.rand(n) * 2,
        "away_conceded_rolling_5": np.random.rand(n),
        "home_win": np.random.choice([0.0, 1.0, 2.0], n),
    })
    trainer = ModelTrainer()
    trainer.train(df, target_col="home_win")
    probs = trainer.predict_proba(df.iloc[:5])
    assert probs.shape == (5, 3)
    np.testing.assert_almost_equal(probs.sum(axis=1), [1.0] * 5)
