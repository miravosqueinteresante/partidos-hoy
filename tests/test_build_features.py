import pandas as pd
from src.features.build_features import FeatureBuilder


def test_feature_builder_creates_features():
    df = pd.DataFrame({
        "home_team": ["Arsenal", "Chelsea"],
        "away_team": ["Chelsea", "Arsenal"],
        "home_goals": [2, 0],
        "away_goals": [0, 1],
        "date": pd.to_datetime(["2026-01-01", "2026-01-15"]),
    })
    builder = FeatureBuilder()
    result = builder.build(df)
    assert len(result) == 2
    assert "elo_diff" in result.columns
    assert "home_form_rolling_5" in result.columns
    assert "home_win" in result.columns


def test_target_variable():
    df = pd.DataFrame({
        "home_team": ["A", "B"],
        "away_team": ["B", "A"],
        "home_goals": [2, 0],
        "away_goals": [0, 1],
    })
    builder = FeatureBuilder()
    result = builder.build(df)
    assert list(result["home_win"]) == [2.0, 0.0]
