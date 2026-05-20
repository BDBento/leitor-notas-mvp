import random
import string
from app.auth import gerar_hash_senha

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
from app.schemas import TelegramLoginRequest, TelegramLoginResponse
from app.auth import (
    gerar_hash_senha,
    verificar_senha,
    criar_token_acesso,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UsuarioResponse)
def registrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com este e-mail"
        )

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha)
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


def gerar_senha_temporaria(tamanho=6):
    caracteres = string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))


@router.post("/telegram-login")
def telegram_login(
    dados: TelegramLoginRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.telegram_user_id == dados.telegram_user_id
    ).first()

    senha_temporaria = None

    if not usuario:
        senha_temporaria = gerar_senha_temporaria()

        email_fake = (
            f"telegram_{dados.telegram_user_id}@telegram.local"
        )

        usuario = Usuario(
            nome=dados.nome or f"Usuário Telegram {dados.telegram_user_id}",
            email=email_fake,
            senha_hash=gerar_hash_senha(senha_temporaria),
            telegram_user_id=dados.telegram_user_id,
            telegram_username=dados.username
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    token = criar_token_acesso({
        "sub": str(usuario.id),
        "telegram_user_id": usuario.telegram_user_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "telegram_user_id": usuario.telegram_user_id,
            "telegram_username": usuario.telegram_username
        },
        "senha_temporaria": senha_temporaria
    }


@router.get("/me", response_model=UsuarioResponse)
def meus_dados(usuario_logado: Usuario = Depends(get_current_user)):
    return usuario_logado

@router.post("/telegram-login", response_model=TelegramLoginResponse)
def telegram_login(
    dados: TelegramLoginRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.telegram_user_id == dados.telegram_user_id
    ).first()

    if not usuario:
        usuario = Usuario(
            nome=dados.nome or f"Usuário Telegram {dados.telegram_user_id}",
            email=None,
            senha_hash=None,
            telegram_user_id=dados.telegram_user_id,
            telegram_username=dados.username
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    token = criar_token_acesso({
        "sub": str(usuario.id),
        "telegram_user_id": usuario.telegram_user_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario
    }