from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Existing modules (UNCHANGED)
from app.modules.metadata_generator.router import router as metadata_router
from app.modules.mapping.router import router as mapping_router

# NEW: NL2SQL Conversational API
from app.nl2sql.router import router as nl2sql_router

load_dotenv()

app = FastAPI(
    title="Mapper and NL2SQL",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTERS
# -----------------------------
app.include_router(metadata_router)
app.include_router(mapping_router)
app.include_router(nl2sql_router)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def health():
    return {"status": "ok", "service": "nl2sql"}
