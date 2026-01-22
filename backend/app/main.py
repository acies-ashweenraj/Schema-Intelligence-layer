from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.modules.metadata_generator.router import router as metadata_router
from app.modules.mapping.router import router as mapping_router
from app.modules.Kg.router import router as kg_router
from app.modules.nlp.router import router as nlp_router
from app.modules.nlp_rag.router import router as nlp_rag_router

load_dotenv()

app = FastAPI(title="KG Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metadata_router)
app.include_router(mapping_router)
app.include_router(kg_router)
app.include_router(nlp_router)
app.include_router(nlp_rag_router)

@app.get("/")
def health():
    return {"status": "ok"}
