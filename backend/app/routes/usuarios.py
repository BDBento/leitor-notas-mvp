from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import (
    get_current_user,
    gerar_hash_senha
)
from app.database import get_db
from app.models import Usuario

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


class AlterarSenhaRequest(BaseModel):
    nova_senha: str


@router.put("/alterar-senha")
def alterar_senha(
    dados: AlterarSenhaRequest,
    usuario_logado: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    usuario_logado.senha_hash = gerar_hash_senha(
        dados.nova_senha
    )

    db.commit()

    return {
        "message": "Senha alterada com sucesso"
    }