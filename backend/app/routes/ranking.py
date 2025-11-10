# backend/app/routes/ranking.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from ..ranking.features import build_feature_frame
from ..ranking.predict import predict_scores
from ..config import settings

router = APIRouter(prefix="/ranking", tags=["ranking"])


# --------- ortak yardımcı ----------
def _aggregate_scores(
    prods: pd.DataFrame,
    stats: pd.DataFrame,
    model_path: str,
    normalize: bool = False,
) -> pd.DataFrame:
    feats = build_feature_frame(prods, stats)
    ranked = predict_scores(feats, model_path)  # cols: product_id[, date], score
    out = (
        ranked.groupby("product_id", as_index=False)["score"].mean()
        .merge(prods, left_on="product_id", right_on="id", how="left")
        .sort_values("score", ascending=False, kind="mergesort")
        .reset_index(drop=True)
    )
    if normalize and len(out) > 0:
        s = out["score"]
        rng = float(s.max()) - float(s.min())
        out["score_norm"] = ((s - s.min()) / (rng if rng != 0 else 1.0) * 100).round(1)
    out["rank"] = (out.index + 1).astype(int)
    return out


# --------- 1) dönemsel sıralama ----------
@router.get("/", summary="Ürün bazında skorlanmış sıralama")
def get_ranking(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    top_k: int = Query(20, ge=1, le=100),
    normalize: bool = Query(False, description="Skoru 0–100 ölçekle"),
):
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv")
    if start_date:
        stats = stats[stats["date"] >= start_date]
    if end_date:
        stats = stats[stats["date"] <= end_date]
    if stats.empty:
        return []
    out = _aggregate_scores(prods, stats, settings.MODEL_PATH, normalize)
    cols = ["rank", "product_id", "name", "price", "margin", "score"]
    if "score_norm" in out.columns:
        cols.append("score_norm")
    return out.loc[:, cols].head(top_k).to_dict(orient="records")


# /ranking (slashesiz) alias
@router.get("", include_in_schema=False)
def get_ranking_alias(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    top_k: int = 20,
    normalize: bool = False,
):
    return get_ranking(start_date, end_date, top_k, normalize)


# --------- 2) tek gün sıralama ----------
@router.get("/by_day", summary="Seçilen gün için ürün sıralaması")
def ranking_by_day(
    day: str = Query(..., description="YYYY-MM-DD"),
    top_k: int = Query(20, ge=1, le=100),
    normalize: bool = Query(False, description="Skoru 0–100 ölçekle"),
):
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv")
    stats = stats[stats["date"] == day]
    if stats.empty:
        return []
    out = _aggregate_scores(prods, stats, settings.MODEL_PATH, normalize)
    cols = ["rank", "product_id", "name", "price", "margin", "score"]
    if "score_norm" in out.columns:
        cols.append("score_norm")
    return out.loc[:, cols].head(top_k).to_dict(orient="records")


# --------- 3) CSV dışa aktar ----------
@router.get("/export", summary="Sıralamayı CSV olarak kaydet")
def export_ranking(start_date: str, end_date: str, top_k: int = 50, normalize: bool = False):
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv")
    stats = stats[(stats["date"] >= start_date) & (stats["date"] <= end_date)]
    if stats.empty:
        return {"saved": False, "reason": "no data in range"}
    out = _aggregate_scores(prods, stats, settings.MODEL_PATH, normalize)
    cols = ["rank", "product_id", "name", "price", "margin", "score"]
    if "score_norm" in out.columns:
        cols.append("score_norm")
    out = out.loc[:, cols].head(top_k)

    Path("data/exports").mkdir(parents=True, exist_ok=True)
    fn = f"data/exports/ranking_{start_date}_{end_date}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    out.to_csv(fn, index=False, encoding="utf-8-sig")
    return {"saved": True, "file": fn, "rows": int(len(out))}


# --------- 4) PDF rapor ----------
@router.get("/report", summary="PDF rapor üret ve indir")
def report(
    start_date: str,
    end_date: str,
    top_k: int = Query(20, ge=1, le=100),
    normalize: bool = Query(False, description="Skoru 0–100 ölçekle"),
):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv", parse_dates=["date"])
    stats = stats[
        (stats["date"] >= pd.to_datetime(start_date))
        & (stats["date"] <= pd.to_datetime(end_date))
    ]
    if stats.empty:
        return {"saved": False, "reason": "no data in range"}

    out = _aggregate_scores(prods, stats, settings.MODEL_PATH, normalize).head(top_k)

    Path("data/reports").mkdir(parents=True, exist_ok=True)
    fn = f"data/reports/report_{start_date}_{end_date}_{datetime.now():%Y%m%d_%H%M%S}.pdf"

    doc = SimpleDocTemplate(fn, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Menu AI – Ranking Raporu", styles["Title"]),
        Paragraph(f"Tarih Aralığı: {start_date} → {end_date}", styles["Normal"]),
        Spacer(1, 12),
    ]

    headers = ["#", "Ürün", "Fiyat", "Marj", "Skor"]
    table_cols = ["rank", "name", "price", "margin", "score"]
    if "score_norm" in out.columns:
        headers.append("Skor(0–100)")
        table_cols.append("score_norm")

    data = [headers] + out.loc[:, table_cols].round(4).values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#222")),
        ("TEXTCOLOR",(0,0),(-1,0), colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    story.append(t)
    doc.build(story)
    return FileResponse(fn, media_type="application/pdf", filename=Path(fn).name)


# --------- 5) Zaman serisi ----------
@router.get("/series", summary="Tek ürün için gün bazında skor serisi")
def series(
    product_id: int,
    start_date: str,
    end_date: str,
):
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv", parse_dates=["date"])
    mask = (stats["date"] >= pd.to_datetime(start_date)) & (stats["date"] <= pd.to_datetime(end_date))
    stats = stats.loc[mask]
    if stats.empty:
        return []

    feats = build_feature_frame(prods, stats)
    ranked = predict_scores(feats, settings.MODEL_PATH)  # product_id, date?, score

    ts = ranked[ranked["product_id"] == product_id].copy()
    if "date" in ts.columns:
        ts = ts.groupby("date", as_index=False)["score"].mean().sort_values("date")
        ts["date"] = ts["date"].dt.strftime("%Y-%m-%d")
    else:
        ts = ts.assign(date=None).groupby("date", as_index=False)["score"].mean()

    return ts.to_dict(orient="records")


# --------- 6) Satış payı ----------
@router.get("/share", summary="Satış payı (adet) – pie chart veri")
def share(
    start_date: str,
    end_date: str,
    top_k: int = 10
):
    prods = pd.read_csv("data/raw/products.csv")
    stats = pd.read_csv("data/raw/daily_stats.csv")
    stats = stats[(stats["date"] >= start_date) & (stats["date"] <= end_date)]
    if stats.empty:
        return []

    agg = (
        stats.groupby("product_id", as_index=False)["sales_count"].sum()
        .merge(prods, left_on="product_id", right_on="id", how="left")
        .sort_values("sales_count", ascending=False)
        .head(top_k)
    )
    return agg[["product_id", "name", "sales_count"]].to_dict(orient="records")
