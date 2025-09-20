from fastapi import FastAPI
from core.database import engine
from sqlmodel import SQLModel
from core.configs import settings
from api.v1.endpoints import curso
from api.v1.api import api_router


app = FastAPI(title='Cursos API - Fast API SQLAlchemy')
app.include_router(api_router, prefix=settings.API_V1_STR)


# ap1/v1

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)