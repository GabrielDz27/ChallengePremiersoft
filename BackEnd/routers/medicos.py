from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from pydantic import BaseModel
from sqlalchemy import func

from schemas.contagem import ContagemResponse  # Importando o modelo de resposta
from database import get_db
from models import Medico, Municipio, Estado, Especialidade, Hospital, medicos_hospitais
from schemas import medico as medico_schemas
from schemas.medico import MedicoResponse, MedicoPorLocalResponse, MedicoPorEspecialidadeResponse, MedicoPorEspecialidadePorRegiaoResponse
from schemas.medico import MedicoPorEspecialidadePorHospitalResponse

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

@router.get("/contagem", response_model=ContagemResponse)
def contar_medicos(db: Session = Depends(get_db)):
    total = db.query(Medico).count()
    return ContagemResponse(total_medicos=total)

@router.get("/local", response_model=List[MedicoPorLocalResponse])
def listar_medicos_detalhado(
    db: Session = Depends(get_db),
    limit: Optional[int] = None, uf: Optional[str] = "SC"
):
    stmt = (
        db.query(
            func.count(Medico.codigo).label("total_medicos"),
            Municipio.nome.label("municipio_nome"),
            Estado.uf.label("estado_uf")
        )
        .join(Municipio, Medico.municipio_id == Municipio.codigo_ibge, isouter=True)
        .join(Estado, Municipio.codigo_uf == Estado.codigo_uf, isouter=True).where(Estado.uf == uf)
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


@router.get("/especialidade", response_model=List[MedicoPorEspecialidadeResponse])
def listar_medicos_por_especialidade(
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    # Query ajustada para contar médicos por especialidade
    stmt = (
        db.query(
            Especialidade.nome.label("especialidade_nome"),
            func.count(Medico.codigo).label("total_medicos")  # Contagem de médicos
        )
        .join(Especialidade, Medico.especialidade_id == Especialidade.id, isouter=True)  # LEFT JOIN
        .group_by(Especialidade.nome)  # Agrupando por especialidade
    )

    # Aplicando o limite, se necessário
    if limit:
        stmt = stmt.limit(limit)

    # Executando a consulta e coletando os resultados
    resultados = stmt.all()

    # Montando a resposta
    return [
        MedicoPorEspecialidadeResponse(
            especialidade_nome=row.especialidade_nome,
            total_medicos=row.total_medicos
        )
        for row in resultados
    ]

@router.get("/especialidade/regiao", response_model=List[MedicoPorEspecialidadePorRegiaoResponse])
def listar_medicos_por_especialidade_por_regiao(
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    # Query ajustada para contar médicos por especialidade e região 
    stmt = (
        db.query(
            Especialidade.nome.label("especialidade_nome"),
            Estado.uf.label("estado_uf"),
            func.count(Medico.codigo).label("total_medicos")  # Contagem de médicos
        )
        .join(Especialidade, Medico.especialidade_id == Especialidade.id, isouter=True)  # LEFT JOIN
        .join(Estado, Municipio.codigo_uf == Estado.codigo_uf, isouter=True)
        .group_by(Especialidade.nome, Estado.uf)  # Agrupando por especialidade e estado
    )

    # Aplicando o limite, se necessário
    if limit:
        stmt = stmt.limit(limit)

    # Executando a consulta e coletando os resultados
    resultados = stmt.all()

    # Montando a resposta
    return [
        MedicoPorEspecialidadePorRegiaoResponse(
            especialidade_nome=row.especialidade_nome,
            estado_uf=row.estado_uf,
            total_medicos=row.total_medicos
        )
        for row in resultados
    ]

@router.get("/especialidade/hospital", response_model=List[MedicoPorEspecialidadePorHospitalResponse])
def listar_medicos_por_especialidade_por_hospital(
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    # Query ajustada para contar médicos por especialidade e hospital
    stmt = (
        db.query(
            Especialidade.nome.label("especialidade_nome"),
            Hospital.nome.label("hospital_nome"),
            func.count(Medico.codigo).label("total_medicos")  # Contagem de médicos
        )
        .join(Especialidade, Medico.especialidade_id == Especialidade.id)  # JOIN entre Medico e Especialidade
        .join(medicos_hospitais, medicos_hospitais.c.medico_codigo == Medico.codigo)  # JOIN com tabela intermediária
        .join(Hospital, medicos_hospitais.c.hospital_codigo == Hospital.codigo)  # JOIN entre Hospital e tabela intermediária
        .group_by(Especialidade.nome, Hospital.nome)  # Agrupando por especialidade e hospital
    )

    # Aplicando o limite, se necessário
    if limit:
        stmt = stmt.limit(limit)

    # Executando a consulta e coletando os resultados
    resultados = stmt.all()

    # Montando a resposta
    return [
        MedicoPorEspecialidadePorHospitalResponse(
            especialidade_nome=row.especialidade_nome,
            hospital_nome=row.hospital_nome,
            total_medicos=row.total_medicos
        )
        for row in resultados
    ]
