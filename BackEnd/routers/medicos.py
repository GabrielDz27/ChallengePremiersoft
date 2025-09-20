# routers/medicos.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from database import get_db
from models import Medico
from schemas import medico as medico_schemas
from schemas.medico import MedicoResponse

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.post("/", response_model=MedicoResponse)
def criar_medico(medico: medico_schemas.MedicoCreate, db: Session = Depends(get_db)):
    novo_medico = Medico(
        codigo=uuid4(),
        nome_completo=medico.nome_completo,
        especialidade_id=medico.especialidade_id,
        municipio_id=medico.municipio_id
    )
    db.add(novo_medico)
    db.commit()
    db.refresh(novo_medico)
    return novo_medico

@router.get("/", response_model=list[MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(Medico).all()

@router.get("/{codigo}", response_model=MedicoResponse)
def obter_medico(codigo: str, db: Session = Depends(get_db)):
    medico = db.query(Medico).filter_by(codigo=codigo).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico
