import pandas as pd
from src.features.elo_ratings import EloRatingSystem


def test_initial_rating():
    elo = EloRatingSystem()
    assert elo.get_rating("Arsenal") == 1500.0


def test_match_updates_ratings():
    elo = EloRatingSystem(k=20, home_advantage=100)
    df = pd.DataFrame({
        "home_team": ["Arsenal"],
        "away_team": ["Chelsea"],
        "home_goals": [2],
        "away_goals": [0],
    })
    elo.update_from_matches(df)
    arsenal_rating = elo.get_rating("Arsenal")
    chelsea_rating = elo.get_rating("Chelsea")
    assert arsenal_rating > 1500
    assert chelsea_rating < 1500
    assert abs(arsenal_rating - chelsea_rating) > 0


def test_expected_score():
    elo = EloRatingSystem(home_advantage=100)
    prob = elo.expected_score(1500, 1500)
    assert 0.3 < prob < 0.7


def test_goal_margin_factor():
    elo = EloRatingSystem()
    k_factor = elo._goal_margin_factor(2, 0)
    assert k_factor == 1.0
    k_factor = elo._goal_margin_factor(5, 1)
    assert k_factor > 1.0
