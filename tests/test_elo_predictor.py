import json
import hashlib
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest
from src.models.elo_predictor import EloPredictor


@pytest.fixture
def predictor():
    return EloPredictor()


def test_expected_score_home_favored(predictor):
    score = predictor.expected_score(2000, 1500)
    assert 0.5 < score < 1.0


def test_expected_score_away_favored(predictor):
    score = predictor.expected_score(1500, 2000)
    assert 0.0 < score < 0.5


def test_expected_score_equal_ratings(predictor):
    score = predictor.expected_score(1500, 1500)
    home_adv = 1.0 / (1.0 + 10.0 ** (-100 / 400.0))
    assert score == pytest.approx(home_adv, abs=0.001)


def test_expected_score_home_advantage(predictor):
    score_home = predictor.expected_score(1500, 1500)
    score_no_adv = 1.0 / (1.0 + 10.0 ** (0 / 400.0))
    home_adv = 1.0 / (1.0 + 10.0 ** (-100 / 400.0))
    assert score_home == pytest.approx(home_adv, abs=0.001)
    assert score_home > score_no_adv


def test_predict_proba_sum_to_one(predictor):
    probs = predictor.predict_proba("Spain", "Brazil")
    total = probs["home"] + probs["draw"] + probs["away"]
    assert total == pytest.approx(1.0, abs=0.001)


def test_predict_proba_home_stronger(predictor):
    probs = predictor.predict_proba("Spain", "Cabo Verde")
    assert probs["home"] > probs["away"]
    assert probs["home"] > probs["draw"]


def test_predict_proba_away_stronger(predictor):
    probs = predictor.predict_proba("Cabo Verde", "Spain")
    assert probs["away"] > probs["home"]


def test_predict_proba_minimum_floor(predictor):
    probs = predictor.predict_proba("Spain", "Congo DR")
    assert probs["home"] >= 0.05
    assert probs["away"] >= 0.047
    assert probs["draw"] >= 0.05


def test_get_rating_exact_match(predictor):
    rating = predictor.get_rating("Spain")
    assert rating == 2165


def test_get_rating_missing_team_default(predictor):
    rating = predictor.get_rating("Nonexistent Land")
    assert rating == 1500.0


def test_get_rating_null_team(predictor):
    rating = predictor.get_rating("")
    assert rating == 0.0


def test_get_rating_with_accent(predictor):
    rating = predictor.get_rating("Côte d'Ivoire")
    assert rating > 0


def test_get_rating_normalized_form(predictor):
    rating_normalized = predictor.get_rating("Cote d'Ivoire")
    assert rating_normalized > 0


def test_generate_returns_104_matches(predictor):
    df = pd.DataFrame([
        {"id": 1, "date": "2026-06-11", "home_team": "Spain", "away_team": "Brazil",
         "group": "A", "stage": "group", "league": "World Cup 2026", "venue": "Test"},
        {"id": 2, "date": "2026-06-28", "home_team": None, "away_team": None,
         "group": None, "stage": "round_of_32", "league": "World Cup 2026", "venue": "TBD"},
    ])
    output = json.loads(predictor.generate(df))
    assert len(output["matches"]) == 2
    assert "status" not in output["matches"][0]
    assert output["matches"][1]["status"] == "TBD"
    assert output["matches"][1]["home"] is None
    assert "model" in output
    assert "generated_at" in output
    assert output["model_version"] == "1.0.0-elo"


def test_generate_unique_ids(predictor):
    df = pd.DataFrame([
        {"id": i, "date": "2026-06-28", "home_team": None, "away_team": None,
         "group": None, "stage": "round_of_32", "league": "World Cup 2026", "venue": "TBD"}
        for i in range(5)
    ])
    output = json.loads(predictor.generate(df))
    ids = [m["id"] for m in output["matches"]]
    assert len(set(ids)) == 5


def test_expected_goals_consistent_with_probs(predictor):
    probs = predictor.predict_proba("Argentina", "Saudi Arabia")
    home_xg = probs["home"] * 2.5 + probs["draw"] * 1.0
    away_xg = probs["away"] * 2.5 + probs["draw"] * 1.0
    assert home_xg > away_xg


def test_fallback_ratings_loaded(predictor):
    cote = predictor.get_rating("Cote d'Ivoire")
    assert cote > 0, "Fallback ratings should include Cote d'Ivoire"
