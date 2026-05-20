from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True)
    data_gasto = Column(Date, nullable=True)
    estabelecimento = Column(String(255), nullable=True)
    categoria = Column(String(100), nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=True)
    forma_pagamento = Column(String(100), nullable=True)
    imagem_url = Column(String(500), nullable=True)
    texto_extraido = Column(Text, nullable=True)
    status_processamento = Column(String(50), default="pendente")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    senha_hash = Column(String(255), nullable=True)

    telegram_user_id = Column(String(100), unique=True, index=True, nullable=True)
    telegram_username = Column(String(255), nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    