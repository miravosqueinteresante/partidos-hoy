import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from src.models.trainer import ModelTrainer, FEATURE_COLS
from src.models.calibrator import ProbabilityCalibrator


class PredictionGenerator:
    def __init__(self):
        self.trainer = ModelTrainer()
        self.calibrator = ProbabilityCalibrator()

    def train(self, historical_df: pd.DataFrame):
        self.trainer.train(historical_df)
        X = historical_df[FEATURE_COLS].values
        y = historical_df["home_win"].values
        raw_probs = self.trainer.predict_proba(historical_df)
        self.calibrator.fit(raw_probs, y)

    def generate(self, upcoming_matches: pd.DataFrame,
                 api_predictions: Optional[Dict[str, dict]] = None,
                 use_xgboost: bool = True) -> str:
        if use_xgboost and self.trainer.model is not None:
            raw_probs = self.trainer.predict_proba(upcoming_matches)
            calibrated = self.calibrator.calibrate(raw_probs)
        else:
            n = len(upcoming_matches)
            calibrated = np.full((n, 3), 1.0 / 3.0)

        matches_list = []
        for i, (_, match) in enumerate(upcoming_matches.iterrows()):
            match_id = hashlib.md5(
                f"{match['home_team']}-{match['away_team']}-{match.get('date', '')}".encode()
            ).hexdigest()[:8]

            home_prob = float(calibrated[i][2])
            draw_prob = float(calibrated[i][1])
            away_prob = float(calibrated[i][0])

            home_xg = home_prob * 2.5 + draw_prob * 1.0
            away_xg = away_prob * 2.5 + draw_prob * 1.0

            entry = {
                "id": match_id,
                "home": match["home_team"],
                "away": match["away_team"],
                "league": match.get("league", ""),
                "date": str(match.get("date", "")),
                "probabilities": {
                    "home": round(home_prob, 4),
                    "draw": round(draw_prob, 4),
                    "away": round(away_prob, 4),
                },
                "expected_goals": {
                    "home": round(home_xg, 2),
                    "away": round(away_xg, 2),
                },
                "api_prediction": None,
            }

            team_key = match["home_team"]
            if api_predictions and team_key in api_predictions:
                entry["api_prediction"] = {
                    "home": round(api_predictions[team_key].get("home", 0), 4),
                    "draw": round(api_predictions[team_key].get("draw", 0), 4),
                    "away": round(api_predictions[team_key].get("away", 0), 4),
                }

            matches_list.append(entry)

        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": "1.0.0",
            "brier_score": round(float(self.trainer.brier_score or 0), 4),
            "notes": "Predicciones generadas por XGBoost + Isotonic Regression. "
                     "api_prediction contiene la predicción de API-Football como baseline.",
            "matches": matches_list,
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
