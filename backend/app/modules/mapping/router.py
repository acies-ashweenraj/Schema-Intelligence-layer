import traceback
from fastapi import APIRouter, HTTPException
from .schemas import HybridMappingRequest
from .service import run_hybrid_mapping_service

router = APIRouter(prefix="/mapping", tags=["Mapping Layer"])


@router.post("/hybrid")
def hybrid_mapping(req: HybridMappingRequest):
    try:
        result = run_hybrid_mapping_service(req)
        return {
            "status": "success",
            "generated_at": result.get("generated_at"),
            "saved_file": result.get("saved_file"),
            "table_match_count": result.get("table_match_count"),
            "column_match_count": result.get("column_match_count"),
            "details": result,
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
