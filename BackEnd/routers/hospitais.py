from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from pydantic import BaseModel
from sqlalchemy import func

from schemas.contagem import ContagemResponse  # Importando o modelo de resposta
from database import get_db
from models import Hospital, Municipio, Estado  # Supondo que você tenha essas models
from schemas import hospital as hospital_schemas  # Supondo que você tenha schemas para hospital
from schemas.hospital import HospitalResponse, HospitalPorLocalResponse  # Respostas específicas para hospital

router = APIRouter(prefix="/hospitais", tags=["Hospitais"])

# Criar hospital
@router.post("/", response_model=HospitalResponse)
def criar_hospital(hospital: hospital_schemas.HospitalCreate, db: Session = Depends(get_db)):
    novo_hospital = Hospital(
        codigo=uuid4(),
        nome_hospital=hospital.nome_hospital,
        municipio_id=hospital.municipio_id,
        tipo=hospital.tipo  # Exemplo de campo adicional
    )
    
    db.add(novo_hospital)
    db.commit()
    db.refresh(novo_hospital)
    return novo_hospital

# Listar hospitais
@router.get("/", response_model=list[HospitalResponse])
def listar_hospitais(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, gt=0)
):
    query = db.query(Hospital)
    if limit:
        query = query.limit(limit)
    return query.all()

# Contagem de hospitais
@router.get("/contagem", response_model=ContagemResponse)
def contar_hospitais(db: Session = Depends(get_db)):
    total = db.query(Hospital).count()
    return ContagemResponse(total_medicos=total)

# Listar hospitais por local (município e estado)
@router.get("/local", response_model=List[HospitalPorLocalResponse])
def listar_hospitais_detalhado(
    db: Session = Depends(get_db),
    limit: Optional[int] = None, uf: Optional[str] = None
):
    stmt = (
        db.query(
            func.count(Hospital.codigo).label("total_hospitais"),
            Municipio.nome.label("municipio_nome"),
            Estado.uf.label("estado_uf")
        )
        .join(Municipio, Hospital.municipio_id == Municipio.codigo_ibge, isouter=True)
        .join(Estado, Municipio.codigo_uf == Estado.codigo_uf, isouter=True)
        .where(Estado.uf == uf)
        .group_by(Estado.uf, Municipio.nome)
    )

    if limit:
        stmt = stmt.limit(limit)
    

    resultados = stmt.all()

    return [
        HospitalPorLocalResponse(
            total_hospitais=row.total_hospitais,
            municipio_nome=row.municipio_nome,
            estado_uf=row.estado_uf
        )
        for row in resultados
    ]
