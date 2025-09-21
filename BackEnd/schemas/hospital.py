from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class HospitalCreate(BaseModel):
    nome_hospital: str  # Nome do hospital
    municipio_id: int  # ID do município onde o hospital está localizado
    tipo: str  # Tipo do hospital (público, privado, etc.)

    class Config:
        orm_mode = True  # Para permitir que o SQLAlchemy converta o modelo para Pydantic

class HospitalResponse(BaseModel):
    codigo: UUID  # Código único do hospital (UUID)
    nome_hospital: str  # Nome do hospital
    municipio_id: int  # ID do município onde o hospital está localizado
    tipo: str  # Tipo do hospital (público, privado, etc.)

    class Config:
        orm_mode = True  # Para permitir que o SQLAlchemy converta o modelo para Pydantic

class HospitalPorLocalResponse(BaseModel):
    total_hospitais: int  # Total de hospitais
    estado_uf: str  # Unidade Federativa (UF) do estado

    class Config:
        orm_mode = True  # Para permitir que o SQLAlchemy converta o modelo para Pydantic

