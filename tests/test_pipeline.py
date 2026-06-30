import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.models.elo_predictor import EloPredictor


def test_full_pipeline_from_fixtures():
    with open("data/fixtures_wc2026.json", encoding="utf-8") as f:
        fixtures = json.load(f)

    assert len(fixtures) == 104, "Expected exactly 104 World Cup fixtures"

    df = pd.DataFrame(fixtures)
    predictor = EloPredictor("data/team_ratings.json")
    output = json.loads(predictor.generate(df))

    assert output["model_version"] == "1.0.0-elo"
    assert len(output["matches"]) == 104

    group_matches = [m for m in output["matches"] if m.get("status") != "TBD"]
    tbd_matches = [m for m in output["matches"] if m.get("status") == "TBD"]

    print(f"DEBUG: group_matches={len(group_matches)}, tbd_matches={len(tbd_matches)}, total={len(output['matches'])}")

    assert len(group_matches) == 88, f"Expected 88 matches with teams, got {len(group_matches)}"
    assert len(tbd_matches) == 16, f"Expected 16 TBD matches, got {len(tbd_matches)}"

    ids = [m["id"] for m in output["matches"]]
    assert len(ids) == len(set(ids)), "All match IDs must be unique"

    for m in group_matches:
        p = m["probabilities"]
        total = p["home"] + p["draw"] + p["away"]
        assert abs(total - 1.0) < 0.005, f"Probabilities must sum to 1: {total}"
        assert p["home"] >= 0.05
        assert p["draw"] >= 0.05
        assert p["away"] >= 0.047

    for m in group_matches:
        assert "venue" in m
        assert m["venue"] != "TBD", f"Group match should have real venue: {m['id']}"
        assert "expected_goals" in m
        xg = m["expected_goals"]
        assert xg["home"] > 0
        assert xg["away"] > 0

    for m in tbd_matches:
        assert m["home"] is None
        assert m["away"] is None
        assert m["venue"] == "TBD"


def test_output_json_schema():
    with open("data/fixtures_wc2026.json", encoding="utf-8") as f:
        fixtures = json.load(f)

    df = pd.DataFrame(fixtures)
    predictor = EloPredictor("data/team_ratings.json")
    output = json.loads(predictor.generate(df))

    assert "generated_at" in output
    assert "model_version" in output
    assert "model" in output
    assert "matches" in output
    assert isinstance(output["matches"], list)

    for m in output["matches"]:
        assert "id" in m
        assert "league" in m
        assert "date" in m
        assert "stage" in m
        assert "venue" in m
