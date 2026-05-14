import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from app.auth import get_current_user
from app.models import Usuario

router = APIRouter(prefix="/arquivos", tags=["Arquivos"])

UPLOAD_DIR = "uploads"


@router.get("/{filename}")
def visualizar_arquivo(
    filename: str,
    usuario_logado: Usuario = Depends(get_current_user)
):
    caminho = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(caminho):
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado"
        )

    return FileResponse(caminho)