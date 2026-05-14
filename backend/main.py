from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes import gastos
from app.routes import upload
from app.routes import auth
from app.routes import arquivos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leitor de Notas MVP")


app.include_router(gastos.router)
app.include_router(upload.router)
app.include_router(auth.router)
app.include_router(arquivos.router)


@app.get("/")
def home():
    return {
        "message": "Backend do Leitor de Notas MVP funcionando"
    }