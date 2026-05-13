import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_imagem(file: UploadFile = File(...)):
    
    extensoes_permitidas = [".jpg", ".jpeg", ".png", ".pdf"]

    extensao = os.path.splitext(file.filename)[1].lower()

    if extensao not in extensoes_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não permitido"
        )

    nome_arquivo = f"{uuid.uuid4()}{extensao}"

    caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho_arquivo, "wb") as buffer:
        conteudo = await file.read()
        buffer.write(conteudo)

    return {
        "filename": nome_arquivo,
        "url": f"/arquivos/{nome_arquivo}"
    }