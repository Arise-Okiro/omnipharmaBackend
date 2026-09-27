from fastapi import FastAPI as fapi
from app.models.database import engine, Base
import app.models.schema
# Reads the schema definitions and executes CREATE TABLE IF NOT EXISTS in PostgreSQL
Base.metadata.create_all(bind=engine)
app.models= fapi(
    title="Omnipharma tenant and customers platform",
    description="A system to manage medicines and AI suggestions",
    version="1.0.0"
)
@app.models.get("/")
def home():
    return {"this string returns the default message on opening omnipharma website "}