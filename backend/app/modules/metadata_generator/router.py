import traceback
from fastapi import APIRouter, HTTPException
from .schemas import MetadataGenerateRequest
from .service import run_metadata_generation

router = APIRouter(prefix="/metadata", tags=["Metadata Generator"])

@router.post("/generate")
def generate_metadata(req: MetadataGenerateRequest):
    try:
        result = run_metadata_generation(req)
        return {"status": "success", "saved_file": result.get("saved_file")}
    except Exception as e:
        traceback.print_exc()  # <-- MUST
        raise HTTPException(status_code=500, detail=str(e))
