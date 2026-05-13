from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes import gastos
from app.routes import upload

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leitor de Notas MVP")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(gastos.router)
app.include_router(upload.router)


@app.get("/")
def home():
    return {
        "message": "Backend do Leitor de Notas MVP funcionando"
    }