import os
from dataclasses import dataclass


@dataclass
class Config:
    worldcup_league_id: int = 1
    worldcup_season: int = 2026

    api_football_key: str = os.getenv("API_FOOTBALL_KEY", "")
    api_football_base: str = "https://v3.football.api-sports.io"
    api_football_rate_limit: int = 10
    api_football_daily_limit: int = 100

    fbref_wc_url: str = "https://fbref.com/en/comps/1/2026/schedule/2026-World-Cup-Schedule"

    football_data_org_key: str = os.getenv("FOOTBALL_DATA_ORG_KEY", "")
    football_data_org_base: str = "https://api.football-data.org/v4"
    football_data_org_rate_limit: int = 10

    historical_data_dir: str = "data/historical"
    data_dir: str = "data"
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    predictions_dir: str = "predictions"
    model_dir: str = "models/weights"

    min_matches_for_training: int = 50
    test_size: float = 0.15
    random_state: int = 42

    brier_threshold: float = 0.22
    psi_threshold: float = 0.25
    prediction_cache_ttl: int = 21600


config = Config()
