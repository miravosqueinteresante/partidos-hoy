import json
import pandas as pd
import numpy as np
from src.models.predictor import PredictionGenerator


def test_generates_valid_json(tmp_path):
    matches = pd.DataFrame({
        "home_team": ["Arsenal"],
        "away_team": ["Chelsea"],
        "elo_diff": [50.0],
        "home_elo": [1550.0],
        "away_elo": [1500.0],
        "home_form_rolling_5": [2.4],
        "away_form_rolling_5": [1.8],
        "home_goals_rolling_5": [1.8],
        "home_conceded_rolling_5": [0.6],
        "away_goals_rolling_5": [1.5],
        "away_conceded_rolling_5": [0.8],
        "league": ["Premier League"],
        "date": ["2026-06-01"],
    })
    generator = PredictionGenerator()
    result = generator.generate(matches)
    parsed = json.loads(result)
    assert "generated_at" in parsed
    assert "matches" in parsed
    assert len(parsed["matches"]) == 1
    m = parsed["matches"][0]
    assert set(m.keys()) == {"id", "home", "away", "league", "date",
                              "probabilities", "expected_goals",
                              "api_prediction"}
    assert abs(sum(m["probabilities"].values()) - 1.0) < 0.01


def test_json_includes_api_prediction_when_provided():
    matches = pd.DataFrame({
        "home_team": ["Argentina"],
        "away_team": ["Brasil"],
    })
    api_preds = {"Argentina": {"home": 0.40, "draw": 0.30, "away": 0.30}}
    generator = PredictionGenerator()
    result = json.loads(generator.generate(
        matches, api_predictions=api_preds, use_xgboost=False
    ))
    assert result["matches"][0]["api_prediction"]["home"] == 0.40
    assert result["matches"][0]["probabilities"]["home"] == 0.3333
