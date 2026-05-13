from fastapi import FastAPI

app = FastAPI(title="Leitor de Notas MVP")

@app.get("/")
def home():
    return {
        "message": "Backend do Leitor de Notas MVP funcionando"
    }