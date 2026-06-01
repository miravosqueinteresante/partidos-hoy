import pandas as pd
import numpy as np


class RollingStatsCalculator:
    def __init__(self, window: int = 5):
        self.window = window

    def _points_from_result(self, home_goals: int, away_goals: int,
                            is_home: bool = True) -> int:
        if home_goals > away_goals:
            return 3 if is_home else 0
        elif home_goals == away_goals:
            return 1
        else:
            return 0 if is_home else 3

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        all_teams = pd.unique(df[["home_team", "away_team"]].values.ravel())

        for team in all_teams:
            team_matches = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()
            team_matches["team_goals"] = np.where(
                team_matches["home_team"] == team,
                team_matches["home_goals"], team_matches["away_goals"]
            )
            team_matches["team_conceded"] = np.where(
                team_matches["home_team"] == team,
                team_matches["away_goals"], team_matches["home_goals"]
            )
            team_matches["team_points"] = team_matches.apply(
                lambda r: self._points_from_result(
                    r["home_goals"] if r["home_team"] == team else r["away_goals"],
                    r["away_goals"] if r["home_team"] == team else r["home_goals"],
                    is_home=(r["home_team"] == team)
                ), axis=1
            )

            goals_rolling = team_matches["team_goals"].rolling(self.window, min_periods=1).mean()
            conceded_rolling = team_matches["team_conceded"].rolling(self.window, min_periods=1).mean()
            form_rolling = team_matches["team_points"].rolling(self.window, min_periods=1).mean()

            home_mask = df["home_team"] == team
            away_mask = df["away_team"] == team
            team_indices = team_matches.index

            for idx in team_indices:
                if home_mask[idx]:
                    result.loc[idx, f"home_goals_rolling_{self.window}"] = goals_rolling.loc[idx]
                    result.loc[idx, f"home_conceded_rolling_{self.window}"] = conceded_rolling.loc[idx]
                    result.loc[idx, f"home_form_rolling_{self.window}"] = form_rolling.loc[idx]
                elif away_mask[idx]:
                    result.loc[idx, f"away_goals_rolling_{self.window}"] = goals_rolling.loc[idx]
                    result.loc[idx, f"away_conceded_rolling_{self.window}"] = conceded_rolling.loc[idx]
                    result.loc[idx, f"away_form_rolling_{self.window}"] = form_rolling.loc[idx]

        return result.fillna(0)
