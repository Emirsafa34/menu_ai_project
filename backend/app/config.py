from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()
class Settings(BaseModel):
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./model/artifacts/lgbm_lambdarank.txt")
settings = Settings()
