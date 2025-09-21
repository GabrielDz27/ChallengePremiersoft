from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4

from database import get_db
from models import Paciente
from schemas import paciente as paciente_schemas
from schemas.paciente import PacienteResponse

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("/", response_model=PacienteResponse)
def criar_paciente(paciente: paciente_schemas.PacienteCreate, db: Session = Depends(get_db)):
    novo_paciente = Paciente(
        codigo=uuid4(),
        cpf=paciente.cpf,
        nome_completo=paciente.nome_completo,
        genero=paciente.genero,
        municipio_id=paciente.municipio_id,
        bairro=paciente.bairro,
        convenio=paciente.convenio,
        cid10_id=paciente.cid10_id
    )
    
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)
    return novo_paciente


@router.get("/", response_model=list[PacienteResponse])
def listar_pacientes(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, gt=0),
    count_only: Optional[bool] = Query(False)
):
    if count_only:
        total = db.query(Paciente).count()
        return {"total_pacientes": total}

    query = db.query(Paciente)
    if limit:
        query = query.limit(limit)
    return query.all()


@router.get("/{codigo}", response_model=PacienteResponse)
def obter_paciente(codigo: str, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter_by(codigo=codigo).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente
