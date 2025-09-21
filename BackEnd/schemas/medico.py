# schemas/medico.py

from pydantic import BaseModel, UUID4
from typing import Optional

class MedicoBase(BaseModel):
    nome: str
    especialidade_id: int
    municipio_id: int

class MedicoCreate(MedicoBase):
    pass

class MedicoResponse(MedicoBase):
    codigo: UUID4

    model_config = {
        "from_attributes": True
    }

class MedicoPorLocalResponse(BaseModel):
    total_medicos: int
    municipio_nome: Optional[str] = None
    estado_uf: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class MedicoPorEspecialidadeResponse(BaseModel):
    especialidade_nome: str  # Nome da especialidade
    total_medicos: int  # Total de médicos na especialidade

    class Config:
        # Tornar os campos compatíveis com o formato de resposta JSON
        orm_mode = True


class MedicoPorEspecialidadePorRegiaoResponse(BaseModel):
    estado_uf: str  # Unidade Federativa (UF) do estado
    especialidade_nome: str  # Nome da especialidade
    total_medicos: int  # Total de médicos na especialidade

    class Config:
        # Tornar os campos compatíveis com o formato de resposta JSON
        orm_mode = True

class MedicoPorEspecialidadePorHospitalResponse(BaseModel):
    hospital_nome: str  # Nome do hospital
    especialidade_nome: str  # Nome da especialidade
    total_medicos: int  # Total de médicos na especialidade

    class Config:
        # Tornar os campos compatíveis com o formato de resposta JSON
        orm_mode = True