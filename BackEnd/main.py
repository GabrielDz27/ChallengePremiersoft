from fastapi import FastAPI
from routers import pacientes  # importa o módulo pacientes.py

app = FastAPI()

app.include_router(pacientes.router)
# Inclua outros routers conforme necessário

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)