from typing import List, Optional
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit


FEATURE_COLS = [
    "elo_diff", "home_elo", "away_elo",
    "home_form_rolling_5", "away_form_rolling_5",
    "home_goals_rolling_5", "home_conceded_rolling_5",
    "away_goals_rolling_5", "away_conceded_rolling_5",
]

TARGET_MAP = {0: "away", 1: "draw", 2: "home"}


class ModelTrainer:
    def __init__(self):
        self.model: Optional[xgb.XGBClassifier] = None
        self.feature_cols: List[str] = FEATURE_COLS
        self.brier_score: Optional[float] = None

    def train(self, df: pd.DataFrame, target_col: str = "home_win"):
        X = df[self.feature_cols].values
        y = df[target_col].values

        tscv = TimeSeriesSplit(n_splits=3)
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=2,
        )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict_proba(X_val)
        self.brier_score = np.mean((y_pred - np.eye(3)[y_val.astype(int)]) ** 2)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not trained yet")
        X = df[self.feature_cols].values
        return self.model.predict_proba(X)

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        return dict(zip(
            self.feature_cols,
            self.model.feature_importances_.tolist()
        ))
