import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

from .schemas import MetadataRequest
from .service import run_metadata_generation

router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.post("/generate")
def generate_metadata(payload: MetadataRequest):
    return run_metadata_generation(payload, output_dir=payload.output_dir)


@router.get("/download")
def download_metadata(path: str = Query(...)):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path,
        filename=os.path.basename(path),
        media_type="application/octet-stream",
    )
