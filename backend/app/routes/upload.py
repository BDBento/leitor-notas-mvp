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
    extrair_estabelecimento,
    classificar_categoria,
)

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024

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
            detail="Formato de arquivo não permitido. Envie JPG, PNG ou PDF."
        )

    conteudo = await file.read()

    if len(conteudo) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. O limite é 10MB."
        )

    nome_arquivo = f"{uuid.uuid4()}{extensao}"
    caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho_arquivo, "wb") as buffer:
        buffer.write(conteudo)

    texto_extraido = None
    valor_total = None
    data_gasto = None
    estabelecimento = None
    categoria = "Outros"
    status_processamento = "pendente"

    try:
        texto_extraido = executar_ocr(caminho_arquivo)

        valor_total = extrair_valor(texto_extraido)
        data_gasto = extrair_data(texto_extraido)
        estabelecimento = extrair_estabelecimento(texto_extraido)
        categoria = classificar_categoria(texto_extraido)

        status_processamento = "processado"

    except Exception as erro:
        texto_extraido = f"Erro ao processar OCR: {str(erro)}"
        status_processamento = "erro"

    novo_gasto = Gasto(
        usuario_id=usuario_logado.id,
        imagem_url=f"/arquivos/{nome_arquivo}",
        texto_extraido=texto_extraido,
        valor_total=valor_total,
        data_gasto=data_gasto,
        estabelecimento=estabelecimento,
        categoria=categoria,
        status_processamento=status_processamento
    )

    db.add(novo_gasto)
    db.commit()
    db.refresh(novo_gasto)

    return {
        "message": "Imagem enviada com sucesso",
        "gasto_id": novo_gasto.id,
        "filename": nome_arquivo,
        "url": f"/arquivos/{nome_arquivo}",
        "status": novo_gasto.status_processamento,
        "valor_total": str(novo_gasto.valor_total) if novo_gasto.valor_total else None,
        "data_gasto": str(novo_gasto.data_gasto) if novo_gasto.data_gasto else None,
        "estabelecimento": novo_gasto.estabelecimento
    }