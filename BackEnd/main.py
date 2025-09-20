from sys import prefix
from fastapi import FastAPI
from routers import medicos

app = FastAPI()

prefix="/api/v1"

#app.include_router(pacientes.router)
app.include_router(medicos.router, prefix=prefix)

# Inclua outros routers conforme necessário

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)