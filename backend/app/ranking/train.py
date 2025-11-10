import pandas as pd, numpy as np, lightgbm as lgb
from joblib import dump
from pathlib import Path
from .features import build_feature_frame

if __name__ == "__main__":
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv", parse_dates=["date"])

    df = build_feature_frame(prods, stats)

    # ham skor: brüt gelir ~ price * margin * sales_count
    df["raw"] = df["price"] * df["margin"] * df["sales_count"]

    # grup: gün bazında sıralama yapacağız
    df["group"] = df["date"].astype(str)

    # Integer label 0..4 üret (gün içi yüzde sırasına göre)
    # pct rank -> [0,1]; *5 -> [0,5); int -> {0,1,2,3,4}
    df["label"] = df.groupby("group")["raw"].transform(lambda s: (s.rank(pct=True) * 5 - 1e-9).astype(int))

    feature_cols = ["price","margin","sales_count","cr","unit_profit","aov","ppc","is_signature"]
    X = df[feature_cols].values
    y = df["label"].values

    # LightGBM grup büyüklükleri
    qid = df["group"].astype("category").cat.codes
    group_sizes = np.bincount(qid)

    train_data = lgb.Dataset(X, label=y, group=group_sizes)
    params = dict(
        objective="lambdarank",
        metric="ndcg",
        ndcg_eval_at=[5,10],
        learning_rate=0.05,
        num_leaves=31,
        # İsteğe bağlı: 2^label - 1 kazançları
        label_gain=[0,1,3,7,15]
    )
    model = lgb.train(params, train_data, num_boost_round=150)

    Path("model/artifacts").mkdir(parents=True, exist_ok=True)
    model.save_model("model/artifacts/lgbm_lambdarank.txt")
    dump(feature_cols, "model/artifacts/lgbm_lambdarank.txt.features.joblib")
    print("Model kaydedildi: model/artifacts/lgbm_lambdarank.txt")
