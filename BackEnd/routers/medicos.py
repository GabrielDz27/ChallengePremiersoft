from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from pydantic import BaseModel
from sqlalchemy import func

from database import get_db
from models import Medico, Municipio, Estado
from schemas import medico as medico_schemas
from schemas.medico import MedicoResponse, MedicoPorLocalResponse  

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
def listar_medicos(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, gt=0)
):
    query = db.query(Medico)
    if limit:
        query = query.limit(limit)
    return query.all()

@router.get("/contagem", response_model=dict)
def contar_medicos(db: Session = Depends(get_db)):
    total = db.query(Medico).count()
    return {"total_medicos": total}

@router.get("/local", response_model=List[MedicoPorLocalResponse])
def listar_medicos_detalhado(
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    stmt = (
        db.query(
            func.count(Medico.codigo).label("total_medicos"),
            Municipio.nome.label("municipio_nome"),
            Estado.uf.label("estado_uf")
        )
        .join(Municipio, Medico.municipio_id == Municipio.codigo_ibge, isouter=True)
        .join(Estado, Municipio.codigo_uf == Estado.codigo_uf, isouter=True)
        .group_by(Estado.uf, Municipio.nome)
    )

    if limit:
        stmt = stmt.limit(limit)

    resultados = stmt.all()

    return [
        MedicoPorLocalResponse(
            total_medicos=row.total_medicos,
            municipio_nome=row.municipio_nome,
            estado_uf=row.estado_uf
        )
        for row in resultados
    ]
