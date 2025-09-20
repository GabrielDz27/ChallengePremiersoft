# schemas.py
from pydantic import BaseModel
from typing import Optional
import uuid

class PacienteCreate(BaseModel):
    cpf: str
    nome_completo: str
    genero: Optional[str] = None
    municipio_id: int
    bairro: Optional[str] = None
    convenio: Optional[str] = None
    cid10_id: int

class PacienteResponse(PacienteCreate):
    codigo: uuid.UUID

    class Config:
        orm_mode = True
