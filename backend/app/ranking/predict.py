# backend/app/ranking/predict.py
import pandas as pd
import lightgbm as lgb
from joblib import load


def predict_scores(df_feat: pd.DataFrame, model_path: str) -> pd.DataFrame:
    """Model skorlarını üretir. 'date' kolonu varsa sonuçta korunur."""
    model = lgb.Booster(model_file=model_path)
    feature_cols = load(model_path + ".features.joblib")

    scores = model.predict(df_feat[feature_cols].values)

    out = df_feat[["product_id"]].copy()
    if "date" in df_feat.columns:
        out["date"] = df_feat["date"]  # zaman serisi endpointi için gerekli
    out["score"] = scores
    return out.sort_values("score", ascending=False)
