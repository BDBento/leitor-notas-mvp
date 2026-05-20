import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import (
    UsuarioCreate,
    UsuarioResponse,
    LoginRequest,
    TokenResponse,
    TelegramLoginRequest,
)
from app.auth import (
    gerar_hash_senha,
    verificar_senha,
    criar_token_acesso,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def gerar_senha_temporaria(tamanho=6):
    caracteres = string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


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


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email == dados.email.strip()
    ).first()

    if not usuario or not usuario.senha_hash:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    if not verificar_senha(dados.senha.strip(), usuario.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    token = criar_token_acesso({
        "sub": str(usuario.id),
        "email": usuario.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


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
        email_fake = f"telegram_{dados.telegram_user_id}@telegram.local"

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

    else:
        atualizou = False

        if not usuario.email:
            usuario.email = f"telegram_{dados.telegram_user_id}@telegram.local"
            atualizou = True

        if not usuario.senha_hash:
            senha_temporaria = gerar_senha_temporaria()
            usuario.senha_hash = gerar_hash_senha(senha_temporaria)
            atualizou = True

        if dados.nome:
            usuario.nome = dados.nome
            atualizou = True

        if dados.username:
            usuario.telegram_username = dados.username
            atualizou = True

        if atualizou:
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


@router.post("/telegram-reset-password")
def telegram_reset_password(
    dados: TelegramLoginRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.telegram_user_id == dados.telegram_user_id
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário Telegram não encontrado"
        )

    senha_temporaria = gerar_senha_temporaria()

    if not usuario.email:
        usuario.email = f"telegram_{dados.telegram_user_id}@telegram.local"

    usuario.senha_hash = gerar_hash_senha(senha_temporaria)

    db.commit()
    db.refresh(usuario)

    return {
        "email": usuario.email,
        "senha_temporaria": senha_temporaria
    }


@router.get("/me", response_model=UsuarioResponse)
def meus_dados(usuario_logado: Usuario = Depends(get_current_user)):
    return usuario_logado