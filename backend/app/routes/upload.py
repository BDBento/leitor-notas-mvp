import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Usuario, Gasto

from app.services.ocr_service import executar_ocr
from app.services.parser_service import (
    extrair_valor,
    extrair_data,
    extrair_estabelecimento
)

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_imagem(
    file: UploadFile = File(...),
    usuario_logado: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    texto_extraido = executar_ocr(caminho_arquivo)

    valor_total = extrair_valor(texto_extraido)
    data_gasto = extrair_data(texto_extraido)
    estabelecimento = extrair_estabelecimento(texto_extraido)

    novo_gasto = Gasto(
        usuario_id=usuario_logado.id,
        imagem_url=f"/arquivos/{nome_arquivo}",
        texto_extraido=texto_extraido,
        valor_total=valor_total,
        data_gasto=data_gasto,
        estabelecimento=estabelecimento,
        status_processamento="processado"
    )

    db.add(novo_gasto)
    db.commit()
    db.refresh(novo_gasto)

    return {
        "message": "Imagem enviada com sucesso",
        "gasto_id": novo_gasto.id,
        "filename": nome_arquivo,
        "url": f"/arquivos/{nome_arquivo}",
        "status": novo_gasto.status_processamento
    }
    
    