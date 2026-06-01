from typing import Dict
import pandas as pd
import numpy as np


class EloRatingSystem:
    def __init__(self, k: float = 20, home_advantage: float = 100):
        self.k = k
        self.home_advantage = home_advantage
        self.ratings: Dict[str, float] = {}

    def get_rating(self, team: str) -> float:
        return self.ratings.get(team, 1500.0)

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        diff = rating_a - rating_b + self.home_advantage
        return 1.0 / (1.0 + 10 ** (-diff / 400.0))

    def _goal_margin_factor(self, home_goals: int, away_goals: int) -> float:
        goal_diff = abs(home_goals - away_goals)
        if goal_diff <= 2:
            return 1.0
        return 1.0 + (goal_diff - 2) * 0.1

    def update(self, home_team: str, away_team: str,
               home_goals: int, away_goals: int):
        home_rating = self.get_rating(home_team)
        away_rating = self.get_rating(away_team)

        expected_home = self.expected_score(home_rating, away_rating)
        expected_away = 1 - expected_home

        home_won = 1 if home_goals > away_goals else (0.5 if home_goals == away_goals else 0)
        away_won = 1 - home_won

        margin = self._goal_margin_factor(home_goals, away_goals)

        self.ratings[home_team] = home_rating + self.k * margin * (home_won - expected_home)
        self.ratings[away_team] = away_rating + self.k * margin * (away_won - expected_away)

    def update_from_matches(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            self.update(
                row["home_team"], row["away_team"],
                int(row["home_goals"]), int(row["away_goals"])
            )

    def get_rating_diff_feature(self, home_team: str, away_team: str) -> float:
        return self.get_rating(home_team) - self.get_rating(away_team)
