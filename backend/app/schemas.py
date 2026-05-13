from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class GastoBase(BaseModel):
    data_gasto: Optional[date] = None
    estabelecimento: Optional[str] = None
    categoria: Optional[str] = None
    valor_total: Optional[Decimal] = None
    forma_pagamento: Optional[str] = None
    imagem_url: Optional[str] = None
    texto_extraido: Optional[str] = None
    status_processamento: Optional[str] = "pendente"


class GastoCreate(GastoBase):
    pass


class GastoUpdate(GastoBase):
    pass


class GastoResponse(GastoBase):
    id: int
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"