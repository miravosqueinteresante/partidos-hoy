import os
from dataclasses import dataclass


@dataclass
class Config:
    data_dir: str = "data"
    fixtures_path: str = "data/fixtures_wc2026.json"
    ratings_path: str = "data/team_ratings.json"
    predictions_dir: str = "predictions"
    home_advantage: int = 100
    elo_k_factor: int = 400


config = Config()
