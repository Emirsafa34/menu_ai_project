from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, ranking

app = FastAPI(
    title="MenuAI",
    description="Yapay zekâ destekli menü sıralama API’si",
    version="1.0.0",
)

# === Router’lar ===
app.include_router(health.router)
app.include_router(ranking.router)

# === CORS ayarları ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # React (Vite) dev server erişimi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Root ===
@app.get("/")
def root():
    return {"message": "MenuAI backend aktif", "docs": "/docs"}
