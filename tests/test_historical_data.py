import pandas as pd
import pytest
from src.data.historical_data import HistoricalDataParser


def test_parse_csv_with_valid_data(tmp_path):
    csv_content = "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HST,AST,HC,AC\n"
    csv_content += "E0,01/06/26,Arsenal,Chelsea,2,1,H,5,3,7,4\n"
    csv_content += "E0,02/06/26,Man City,Liverpool,1,1,D,4,6,5,8\n"
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(csv_content)

    parser = HistoricalDataParser()
    df = parser.load_csv(str(csv_file))
    assert len(df) == 2
    assert list(df.columns) == ["league", "date", "home_team", "away_team",
                                 "home_goals", "away_goals", "result",
                                 "home_shots_target", "away_shots_target",
                                 "home_corners", "away_corners"]


def test_filter_by_league():
    data = {
        "league": ["E0", "E0", "E1", "E1"],
        "home_team": ["A", "B", "C", "D"],
        "away_team": ["B", "A", "D", "C"],
    }
    df = pd.DataFrame(data)
    parser = HistoricalDataParser()
    result = parser.filter_league(df, "E0")
    assert len(result) == 2
