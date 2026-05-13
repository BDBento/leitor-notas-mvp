import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/arquivos", tags=["Arquivos"])

UPLOAD_DIR = "uploads"


@router.get("/{filename}")
def visualizar_arquivo(filename: str):
    caminho = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(caminho)