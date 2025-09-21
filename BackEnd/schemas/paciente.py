from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class PacienteCreate(BaseModel):
    nome_completo: str
    cpf: str
    municipio_id: int
    cid10_id: int

    class Config:
        orm_mode = True

class PacienteResponse(BaseModel):
    codigo: UUID
    nome_completo: str
    cpf: str
    municipio_id: int
    cid10_id: int

    class Config:
        orm_mode = True

# Caso você queira incluir a descrição da doença (CID-10) no retorno
class PacienteDetalhadoResponse(PacienteResponse):
    nome_doenca: str
    descricao_doenca: str

    class Config:
        orm_mode = True


class DoencaContagemResponse(BaseModel):
    descricao_doenca: str
    total_pacientes: int

    class Config:
            orm_mode = True