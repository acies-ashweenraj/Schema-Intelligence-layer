import traceback
from fastapi import APIRouter, HTTPException
from .schemas import KGLoadRequest
from .service import load_kg

router = APIRouter(prefix="/kg", tags=["Knowledge Graph Loader"])

@router.post("/load")
def load_knowledge_graph(req: KGLoadRequest):
    try:
        return load_kg(req)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
