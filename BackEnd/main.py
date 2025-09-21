from sys import prefix
from fastapi import FastAPI
from routers import medicos

app = FastAPI(
redoc_url="/custom-redoc", # Serve ReDoc at /custom-redoc
docs_url=None # Disable Swagger UI
)

prefix="/api/v1"

#app.include_router(pacientes.router)
app.include_router(medicos.router, prefix=prefix)

# Inclua outros routers conforme necessário

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)