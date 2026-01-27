from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine

app = FastAPI(title=settings.app_name)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-ping")
def db_ping():
    # Quick sanity check that Postgres is reachable
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
    return {"db": "ok", "result": result}
