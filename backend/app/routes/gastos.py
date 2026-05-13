from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Gasto
from app.schemas import GastoCreate, GastoUpdate, GastoResponse

router = APIRouter(prefix="/gastos", tags=["Gastos"])


@router.get("/", response_model=list[GastoResponse])
def listar_gastos(db: Session = Depends(get_db)):
    return db.query(Gasto).order_by(Gasto.id.desc()).all()


@router.post("/", response_model=GastoResponse)
def criar_gasto(gasto: GastoCreate, db: Session = Depends(get_db)):
    novo_gasto = Gasto(**gasto.model_dump())
    db.add(novo_gasto)
    db.commit()
    db.refresh(novo_gasto)
    return novo_gasto


@router.get("/{gasto_id}", response_model=GastoResponse)
def buscar_gasto(gasto_id: int, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()

    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")

    return gasto


@router.put("/{gasto_id}", response_model=GastoResponse)
def atualizar_gasto(
    gasto_id: int,
    dados: GastoUpdate,
    db: Session = Depends(get_db)
):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()

    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(gasto, campo, valor)

    db.commit()
    db.refresh(gasto)

    return gasto


@router.delete("/{gasto_id}")
def deletar_gasto(gasto_id: int, db: Session = Depends(get_db)):
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()

    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")

    db.delete(gasto)
    db.commit()

    return {"message": "Gasto removido com sucesso"}