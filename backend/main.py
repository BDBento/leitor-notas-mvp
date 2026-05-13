from fastapi import FastAPI
from app.database import Base, engine
from app.routes import gastos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leitor de Notas MVP")

app.include_router(gastos.router)


@app.get("/")
def home():
    return {
        "message": "Backend do Leitor de Notas MVP funcionando"
    }