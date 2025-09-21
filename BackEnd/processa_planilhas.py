import uuid
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import insert as mysql_insert
from models import Cid10, Base, Especialidade, Estado, Hospital, Municipio, Medico, Paciente
import xml.etree.ElementTree as ET

# ----------------------------
# Configuração do banco
# ----------------------------
DATABASE_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING")
engine = create_engine(DATABASE_CONNECTION_STRING)
Session = sessionmaker(bind=engine)

BATCH_SIZE = 500
PACIENTE_LIMIT = 20000

# ----------------------------
# Função para ler diferentes tipos de arquivo
# ----------------------------
def check_file_type(file_path, skiprows=0, header=0, names=None):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path, skiprows=skiprows, header=header, names=names)
    elif ext == '.csv':
        return pd.read_csv(file_path, skiprows=skiprows, header=header, names=names)
    elif ext == '.xml':
        return ET.parse(file_path)
    elif ext == '.json':
        return pd.read_json(file_path)
    elif ext == '.parquet':
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {ext}")

# ----------------------------
# Função para ler CID10
# ----------------------------
def read_cid10_file(file_path):
    session = Session()
    df = pd.read_excel(file_path, skiprows=2, header=None, names=['raw'])
    categoria_atual = None
    cid10_list = []
    seen_codes = set()

    for raw_text in df['raw']:
        if pd.isna(raw_text):
            continue
        raw_text = str(raw_text).strip()
        if ':' in raw_text:
            categoria_atual = raw_text.split(':', 1)[1].strip()
        elif ' - ' in raw_text:
            codigo, descricao = map(str.strip, raw_text.split(' - ', 1))
            if codigo in seen_codes:
                continue
            seen_codes.add(codigo)
            if session.query(Cid10).filter_by(codigo=codigo).first():
                continue
            cid10_list.append(Cid10(codigo=codigo, descricao=descricao, categoria=categoria_atual))
    
    if cid10_list:
        session.bulk_save_objects(cid10_list)
        session.commit()
    session.close()
    print(f"{len(cid10_list)} CID10s inseridos com sucesso.")

# ----------------------------
# Funções para importar estados e municípios
# ----------------------------
def read_estados(file_path):
    df = pd.read_csv(file_path)
    session = Session()
    for _, row in df.iterrows():
        estado = Estado(
            codigo_uf=int(row['codigo_uf']),
            uf=row['uf'],
            nome=row['nome'],
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            regiao=row['regiao']
        )
        session.merge(estado)
    session.commit()
    session.close()
    print("Estados importados com sucesso.")

def read_municipios(file_path):
    df = pd.read_csv(file_path)
    session = Session()
    for _, row in df.iterrows():
        municipio = Municipio(
            codigo_ibge=int(row['codigo_ibge']),
            nome=row['nome'],
            latitude=float(row['latitude']) if not pd.isna(row['latitude']) else None,
            longitude=float(row['longitude']) if not pd.isna(row['longitude']) else None,
            capital=bool(int(row['capital'])) if not pd.isna(row['capital']) else False,
            codigo_uf=int(row['codigo_uf']),
            siafi_id=int(row['siafi_id']) if not pd.isna(row['siafi_id']) else None,
            ddd=str(row['ddd']) if not pd.isna(row['ddd']) else None,
            fuso_horario=row['fuso_horario'] if not pd.isna(row['fuso_horario']) else None,
            populacao=int(row['populacao']) if not pd.isna(row['populacao']) else None
        )
        session.merge(municipio)
    session.commit()
    session.close()
    print("Municípios importados com sucesso.")

# ----------------------------
# Funções para hospitais e especialidades
# ----------------------------
def read_especialidades(file_path):
    df = check_file_type(file_path)
    especialidades_set = set()
    for esp_str in df['especialidades'].dropna():
        especialidades_set.update([e.strip() for e in esp_str.split(';')])
    
    session = Session()
    for esp_nome in especialidades_set:
        if not session.query(Especialidade).filter_by(nome=esp_nome).first():
            session.add(Especialidade(nome=esp_nome))
    session.commit()
    session.close()
    print(f"{len(especialidades_set)} especialidades inseridas/atualizadas com sucesso!")

def read_hospitais(file_path):
    df = check_file_type(file_path)
    session = Session()
    for _, row in df.iterrows():
        municipio = session.query(Municipio).filter_by(codigo_ibge=int(row['cidade'])).one_or_none()
        if not municipio:
            print(f"Município {row['cidade']} não encontrado. Pulando hospital {row['nome']}")
            continue
        
        hospital = session.query(Hospital).filter_by(codigo=row['codigo']).one_or_none()
        if not hospital:
            hospital = Hospital(codigo=row['codigo'])
        
        hospital.nome = row['nome']
        hospital.municipio = municipio
        hospital.bairro = row.get('bairro', None)
        hospital.leitos_totais = int(row['leitos_totais']) if not pd.isna(row['leitos_totais']) else None
        hospital.especialidades.clear()

        for esp_nome in [e.strip() for e in row.get('especialidades', '').split(';') if e.strip()]:
            esp = session.query(Especialidade).filter_by(nome=esp_nome).one_or_none()
            if not esp:
                esp = Especialidade(nome=esp_nome)
                session.add(esp)
                session.flush()
            hospital.especialidades.append(esp)

        session.merge(hospital)
    session.commit()
    session.close()
    print("Hospitais importados com sucesso!")

# ----------------------------
# Funções para médicos
# ----------------------------
def read_medicos(file_path):
    df = check_file_type(file_path)
    session = Session()
    medicos = []
    for _, row in df.iterrows():
        especialidade = session.query(Especialidade).filter_by(nome=row['especialidade']).first()
        municipio = session.query(Municipio).filter_by(codigo_ibge=row['cidade']).first()
        if not especialidade or not municipio:
            continue

        try:
            codigo_uuid = uuid.UUID(row['codigo'])
        except:
            codigo_uuid = uuid.uuid4()

        medicos.append(Medico(
            codigo=codigo_uuid,
            nome_completo=row['nome_completo'],
            especialidade_id=especialidade.id,
            municipio_id=municipio.codigo_ibge
        ))
    
    if medicos:
        session.bulk_save_objects(medicos)
        session.commit()
    session.close()
    print(f"{len(medicos)} médicos inseridos com sucesso!")

# ----------------------------
# Funções para pacientes
# ----------------------------
def processa_paciente(paciente_elem, session):
    codigo = paciente_elem.findtext("Codigo")
    cpf = paciente_elem.findtext("CPF")
    nome = paciente_elem.findtext("Nome_Completo")
    genero = paciente_elem.findtext("Genero")
    cod_municipio = paciente_elem.findtext("Cod_municipio")
    bairro = paciente_elem.findtext("Bairro")
    convenio = paciente_elem.findtext("Convenio")
    cid10_codigo = paciente_elem.findtext("CID-10").split(" ")[-1]

    cid10 = session.query(Cid10).filter_by(codigo=cid10_codigo).first()
    if not cid10:
        return None

    try:
        codigo_uuid = uuid.UUID(codigo)
    except:
        codigo_uuid = uuid.uuid4()

    return Paciente(
        codigo=codigo_uuid,
        cpf=cpf,
        nome_completo=nome,
        genero=genero,
        municipio_id=cod_municipio,
        bairro=bairro,
        convenio=convenio,
        cid10_id=cid10.codigo
    )

def insert_pacientes_ignore_duplicates(pacientes_batch, session):
    values = [
        {
            'codigo': p.codigo,
            'cpf': p.cpf,
            'nome_completo': p.nome_completo,
            'genero': p.genero,
            'municipio_id': p.municipio_id,
            'bairro': p.bairro,
            'convenio': p.convenio,
            'cid10_id': p.cid10_id
        }
        for p in pacientes_batch
    ]
    if not values:
        return
    stmt = mysql_insert(Paciente).values(values).prefix_with("IGNORE")
    session.execute(stmt)
    session.commit()

def processa_pacientes_arquivo(file_path):
    session = Session()
    contexto = ET.iterparse(file_path, events=("end",))
    pacientes_batch = []
    cont = 0

    for _, elem in contexto:
        if elem.tag == "Paciente":
            paciente = processa_paciente(elem, session)
            elem.clear()
            if paciente:
                pacientes_batch.append(paciente)
                cont += 1

            if len(pacientes_batch) >= BATCH_SIZE:
                insert_pacientes_ignore_duplicates(pacientes_batch, session)
                pacientes_batch.clear()

            if cont >= PACIENTE_LIMIT:
                print(f"Limite de {PACIENTE_LIMIT} pacientes atingido. Interrompendo...")
                break

    if pacientes_batch:
        insert_pacientes_ignore_duplicates(pacientes_batch, session)

    session.close()
    print(f"{cont} pacientes processados com sucesso.")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    # Exemplos de uso:
    read_cid10_file('sheet/tabela CID-10.xlsx')
    read_estados('sheet/estados.csv')
    read_municipios('sheet/municipios.csv')
    read_especialidades('sheet/hospitais.csv')
    read_hospitais('sheet/hospitais.csv')
    read_medicos('sheet/medicos.csv')
    processa_pacientes_arquivo('sheet/pacientes.xml')
