from sys import prefix
from fastapi import FastAPI
from routers import medicos, pacientes, hospitais

app = FastAPI(
)

prefix="/api/v1"

app.include_router(pacientes.router, prefix=prefix)
app.include_router(medicos.router, prefix=prefix)
app.include_router(hospitais.router, prefix=prefix)
# Inclua outros routers conforme necessário

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)