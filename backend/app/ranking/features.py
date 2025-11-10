# backend/app/ranking/features.py
import pandas as pd

# Modelin temel beklediği sayısal sütunlar
BASIC_FEATURES = ["price", "margin", "sales_count", "cr"]

# Ek sayısal özellikler (modele dahil edebilirsin; eğitimde seçtiklerin .features.joblib'la belirlenir)
EXTRA_FEATURES = ["unit_profit", "aov", "ppc", "is_signature"]

# UI için tutacağımız ama modele vermeyeceğimiz örnek kategorik alan
UI_ONLY_CATEGORICAL = ["category"]  # modele girmez

def _mock_enrich_products(df_products: pd.DataFrame) -> pd.DataFrame:
    """Ürün tablosunu ek alanlarla zenginleştirir.
    Not: category UI içindir; unit_profit/aov/ppc/is_signature sayısaldır."""
    cats = ["Roll", "Sandwich", "Salad", "Bowl", "Drink"]

    df = df_products.copy()
    # Güvenli tip dönüşümleri
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["price"] = pd.to_numeric(df.get("price", 0), errors="coerce").astype(float)
    df["margin"] = pd.to_numeric(df.get("margin", 0), errors="coerce").astype(float)

    # UI amaçlı kategori
    df["category"] = df["id"].apply(lambda i: cats[(int(i) - 1) % len(cats)] if pd.notna(i) else "Other")

    # Model için ek sayısal alanlar
    df["is_signature"] = df["id"].apply(lambda x: int(int(x) % 3 == 0) if pd.notna(x) else 0)
    df["ppc"] = 0.5  # placeholder
    df["aov"] = df["price"].astype(float)  # basit tanım
    df["unit_profit"] = (df["price"] * df["margin"]).astype(float)

    return df

def build_feature_frame(df_products: pd.DataFrame, df_stats: pd.DataFrame) -> pd.DataFrame:
    """stats + enriched products birleştir, modelin beklediği sayısal kolonları hazırla.
    'date' varsa korur; yoksa düşer."""
    prod_enriched = _mock_enrich_products(df_products)

    df = df_stats.merge(prod_enriched, left_on="product_id", right_on="id", how="left")
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Sayısal tipleri garanti et
    df["product_id"] = pd.to_numeric(df.get("product_id", 0), errors="coerce").astype("Int64")
    if "date" in df.columns:
        # stats tarafında date string gelebilir; tarih olarak da kullanılabilir
        # ama modeli etkilemez. predict tarafında yalnızca görüntüleme için lazım.
        pass

    # stats tarafı
    df["sales_count"] = pd.to_numeric(df.get("sales_count", 0), errors="coerce").fillna(0).astype(float)
    df["cr"] = pd.to_numeric(df.get("cr", 0), errors="coerce").fillna(0).astype(float)

    # ürün tarafı
    df["price"] = pd.to_numeric(df.get("price", 0), errors="coerce").fillna(0).astype(float)
    df["margin"] = pd.to_numeric(df.get("margin", 0), errors="coerce").fillna(0).astype(float)
    df["unit_profit"] = pd.to_numeric(df.get("unit_profit", 0), errors="coerce").fillna(0).astype(float)
    df["aov"] = pd.to_numeric(df.get("aov", 0), errors="coerce").fillna(0).astype(float)
    df["ppc"] = pd.to_numeric(df.get("ppc", 0.0), errors="coerce").fillna(0.0).astype(float)
    df["is_signature"] = pd.to_numeric(df.get("is_signature", 0), errors="ignore").fillna(0).astype(int)

    # Çıkış kolonları: date varsa başa ekle
    cols = ["product_id"]
    if "date" in df.columns:
        cols.append("date")
    cols += BASIC_FEATURES + EXTRA_FEATURES  # modele fazla sütun gitmesi sorun değil; predict feature listeden seçecek

    df = df[cols].fillna(0)
    return df
