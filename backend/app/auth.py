import os
import bcrypt

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

security = HTTPBearer()


def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")

    salt = bcrypt.gensalt()

    senha_hash = bcrypt.hashpw(senha_bytes, salt)

    return senha_hash.decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        senha_hash.encode("utf-8")
    )


def criar_token_acesso(data: dict):
    dados = data.copy()

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados.update({"exp": expiracao})

    token = jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise credenciais_invalidas

    except JWTError:
        raise credenciais_invalidas

    usuario = db.query(Usuario).filter(
        Usuario.id == int(usuario_id)
    ).first()

    if usuario is None:
        raise credenciais_invalidas

    return usuario