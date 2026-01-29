import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
import mimetypes

from .schemas import MetadataRequest
from .service import run_metadata_generation

router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.post("/generate")
def generate_metadata(payload: MetadataRequest):
    return run_metadata_generation(payload)


@router.get("/download")
def download_metadata(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))
