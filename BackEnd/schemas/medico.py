# schemas/medico.py

from pydantic import BaseModel, UUID4
from typing import Optional

class MedicoBase(BaseModel):
    nome_completo: str
    especialidade_id: int
    municipio_id: int

class MedicoCreate(MedicoBase):
    pass

class MedicoResponse(MedicoBase):
    codigo: UUID4

    model_config = {
        "from_attributes": True
    }
