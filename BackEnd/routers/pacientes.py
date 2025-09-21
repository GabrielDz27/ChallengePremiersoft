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
    return ContagemResponse(total_medicos=total)

# Endpoint para contar doenças agrupadas por CID-10
@router.get("/doencas", response_model=List[DoencaContagemResponse])
def contar_doencas(db: Session = Depends(get_db), limit: Optional[int] = 25):
    # 1. Primeira parte: cria a subconsulta para pegar os pacientes
    subquery = (
        db.query(
            Paciente.cid10_id,  # Aqui pegamos o ID da doença associada a cada paciente
            func.count(Paciente.cid10_id).label("total_pacientes")  # Conta os pacientes por doença
        )
        .group_by(Paciente.cid10_id).limit(limit)  # Agrupa pela doença (cid10_id)
        .subquery()  # Converte em uma subconsulta
    )

    # 2. Segunda parte: agora faz o JOIN com a tabela Cid10 para pegar as informações das doenças
    stmt = (
        db.query(
            Cid10.descricao.label("descricao_doenca"),  # Nome da doença
            subquery.c.total_pacientes  # O número de pacientes para cada doença
        )
        .join(subquery, Cid10.codigo == subquery.c.cid10_id)  # Faz o JOIN com a subconsulta (associando a doença com a contagem de pacientes)
    )

    # 4. Executa a consulta e pega os resultados
    resultados = stmt.all()

    # 5. Retorna os resultados no formato adequado
    return [
        DoencaContagemResponse(
            descricao_doenca=row.descricao_doenca,
            total_pacientes=row.total_pacientes
        )
        for row in resultados
    ]
# Exemplo de um possível schema para DoencaContagemResponse
