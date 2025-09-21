from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from sqlalchemy import func
from schemas.contagem import ContagemResponse  # Importando o modelo de resposta

from database import get_db
from models import Paciente, Cid10
from schemas.paciente import PacienteResponse, PacienteCreate, DoencaContagemResponse  

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

# Endpoint para criação de paciente
@router.post("/", response_model=PacienteResponse)
def criar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    novo_paciente = Paciente(
        codigo=uuid4(),
        nome_completo=paciente.nome_completo,
        cpf=paciente.cpf,
        municipio_id=paciente.municipio_id,
        cid10_id=paciente.cid10_id
    )
    
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)
    return novo_paciente

# Endpoint para contar pacientes
@router.get("/contagem", response_model=ContagemResponse)
def contar_pacientes(db: Session = Depends(get_db)):
    total = db.query(Paciente).count()
    return ContagemResponse(total_pacientes=total)

# Endpoint para contar doenças agrupadas por CID-10
@router.get("/doencas", response_model=List[DoencaContagemResponse])
def contar_doencas(db: Session = Depends(get_db), limit: Optional[int] = None):
    stmt = (
        db.query(
            Cid10.descricao.label("descricao_doenca"),
            func.count(Paciente.cid10_id).label("total_pacientes")
        )
        .join(Paciente, Paciente.cid10_id == Cid10.codigo)
        .group_by( Cid10.descricao)
    )

    if limit:
        stmt = stmt.limit(limit)

    resultados = stmt.all()

    return [
        DoencaContagemResponse(
            descricao_doenca=row.descricao_doenca,
            total_pacientes=row.total_pacientes
        )
        for row in resultados
    ]

# Exemplo de um possível schema para DoencaContagemResponse
