from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse
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


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    if not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")

    token = criar_token_acesso({
        "sub": str(usuario.id),
        "email": usuario.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UsuarioResponse)
def meus_dados(usuario_logado: Usuario = Depends(get_current_user)):
    return usuario_logado