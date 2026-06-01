import pandas as pd
import numpy as np
from src.features.elo_ratings import EloRatingSystem
from src.features.rolling_stats import RollingStatsCalculator


class FeatureBuilder:
    def __init__(self, elo_k: float = 20, rolling_window: int = 5):
        self.elo = EloRatingSystem(k=elo_k)
        self.rolling = RollingStatsCalculator(window=rolling_window)
        self._trained = False

    def _create_target(self, df: pd.DataFrame) -> pd.Series:
        result = pd.Series(index=df.index, dtype=float)
        result[df["home_goals"] > df["away_goals"]] = 2.0
        result[df["home_goals"] == df["away_goals"]] = 1.0
        result[df["home_goals"] < df["away_goals"]] = 0.0
        return result

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result = self.rolling.calculate(result)
        self.elo.update_from_matches(df)
        result["elo_diff"] = result.apply(
            lambda r: self.elo.get_rating_diff_feature(r["home_team"], r["away_team"]),
            axis=1
        )
        result["home_elo"] = result["home_team"].apply(lambda t: self.elo.get_rating(t))
        result["away_elo"] = result["away_team"].apply(lambda t: self.elo.get_rating(t))
        result["home_win"] = self._create_target(df)
        result = result.sort_values("date") if "date" in result.columns else result
        return result

    def build_prediction_features(self, home_team: str, away_team: str) -> dict:
        return {
            "elo_diff": self.elo.get_rating_diff_feature(home_team, away_team),
            "home_elo": self.elo.get_rating(home_team),
            "away_elo": self.elo.get_rating(away_team),
        }

    def fit(self, df: pd.DataFrame):
        self.elo = EloRatingSystem(k=20)
        self.elo.update_from_matches(df)
        self._trained = True
