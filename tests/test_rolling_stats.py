import pandas as pd
from src.features.rolling_stats import RollingStatsCalculator


def test_rolling_goals_scored():
    data = {
        "home_team": ["A", "A", "A", "A", "A"],
        "away_team": ["B", "C", "D", "E", "F"],
        "home_goals": [1, 2, 3, 0, 1],
        "away_goals": [0, 1, 1, 2, 0],
    }
    df = pd.DataFrame(data)
    calc = RollingStatsCalculator(window=3)
    result = calc.calculate(df)

    assert "home_goals_rolling_3" in result.columns
    assert "away_goals_rolling_3" in result.columns


def test_form_streak():
    data = {
        "home_team": ["A", "A", "A", "A"],
        "away_team": ["B", "C", "D", "E"],
        "home_goals": [1, 2, 0, 3],
        "away_goals": [0, 0, 1, 1],
    }
    df = pd.DataFrame(data)
    calc = RollingStatsCalculator(window=5)
    result = calc.calculate(df)
    assert "home_form_rolling_5" in result.columns
    assert result["home_form_rolling_5"].iloc[-1] > 0
