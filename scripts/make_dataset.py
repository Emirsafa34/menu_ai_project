# scripts/make_dataset.py
import os
import numpy as np
import pandas as pd

os.makedirs("data/raw", exist_ok=True)
rng = np.random.default_rng(42)  # deterministik

# Gerçek ürün isimleri (deniz ürünleri örnek)
NAMES = [
    "Levrek Ekmek",
    "Somon Izgara",
    "Çupra Tava",
    "Karides Güveç",
    "Kalamar Tava",
    "Midye Dolma",
    "Sardalya Izgara",
    "Uskumru Tava",
    "Hamsi Tava",
    "Lagos Izgara",
]

# Ürün kataloğu
products = pd.DataFrame({
    "id": np.arange(1, len(NAMES) + 1),
    "name": NAMES,
    # fiyat: 120–300 arası, TL
    "price": rng.integers(120, 300, size=len(NAMES)).astype(int),
    # marj: %20–%55
    "margin": np.round(rng.uniform(0.20, 0.55, size=len(NAMES)), 2),
})
products.to_csv("data/raw/products.csv", index=False)

# Günlük satış istatistikleri (Eylül 2025)
dates = pd.date_range("2025-09-01", "2025-09-30")
rows = []
for d in dates:
    for pid in products["id"]:
        sales = int(rng.integers(0, 40))          # günlük adet
        cr = float(rng.uniform(0.05, 0.25))       # conversion rate
        rows.append((pid, str(d.date()), sales, cr))

stats = pd.DataFrame(rows, columns=["product_id", "date", "sales_count", "cr"])
stats.to_csv("data/raw/daily_stats.csv", index=False)

print("Veriler yazıldı -> data/raw/products.csv, data/raw/daily_stats.csv")
