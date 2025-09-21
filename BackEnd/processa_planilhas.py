import uuid
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Cid10, Base, Especialidade, Estado, Hospital, Municipio, Medico, Paciente 
import xml.etree.ElementTree as ET
import os
from sqlalchemy.dialects.mysql import insert as mysql_insert



def check_file_type(file_path, skiprows=0, header=0, names=None):
   ft = os.path.splitext(file_path)[1].lower()
   if ft in ['.xlsx', '.xls']:
       return pd.read_excel(file_path, skiprows=skiprows, header=header, names=names)
   elif ft == '.csv':
       return pd.read_csv(file_path, skiprows=skiprows, header=header, names=names)
   elif ft == '.xml':
       return ET.parse(file_path)
   elif ft == '.json':
       return pd.read_json(file_path)
   elif ft == '.parquet':   
       return pd.read_parquet(file_path)

DATABASE_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(DATABASE_CONNECTION_STRING)
Session = sessionmaker(bind=engine)
session = Session()

def read_cid10_file(file_path, session):
    # Ler o arquivo Excel, pulando as 2 primeiras linhas (header na linha 3)
    df = pd.read_excel(file_path, skiprows=2, header=None, names=['raw'])

    categoria_atual = None
    cid10_list = []
    seen_codes = set()  # Usado para armazenar códigos já processados, evitando duplicados

    for raw_text in df['raw']:
        if pd.isna(raw_text):
            continue  # Pula linhas vazias
        
        raw_text = str(raw_text).strip()
        
        # Linha de categoria (exemplo: "Categoria: Cardiologia")
        if ':' in raw_text:
            # Define a categoria atual com o texto após os dois pontos
            categoria_atual = raw_text.split(':', 1)[1].strip()
        else:
            # Linha que deve ser código - descrição (exemplo: "A00 - Cólera")
            if ' - ' in raw_text:
                codigo, descricao = raw_text.split(' - ', 1)
                codigo = codigo.strip()
                descricao = descricao.strip()
                
                # Verifica se o código CID10 já foi adicionado
                if codigo in seen_codes:
                    continue  # Ignora se o código já foi processado
                seen_codes.add(codigo)  # Marca o código como processado

                # Verifica se o código CID10 já existe no banco
                cid10_existente = session.query(Cid10).filter_by(codigo=codigo).first()
                if cid10_existente:
                    continue  # Se o código já existe no banco, pula a inserção

                # Cria o objeto Cid10
                cid10 = Cid10(codigo=codigo, descricao=descricao, categoria=categoria_atual)
                cid10_list.append(cid10)

    # Salvar os CID10 no banco de dados de forma eficiente (evita duplicação)
    if cid10_list:
        session.bulk_save_objects(cid10_list)
        session.commit()

    print(f"{len(cid10_list)} CID10s inseridos com sucesso.")

def read_estados(file_path):
    df = pd.read_csv(file_path)
    with Session() as session:
        for _, row in df.iterrows():
            estado = Estado(
                codigo_uf=int(row['codigo_uf']),
                uf=row['uf'],
                nome=row['nome'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                regiao=row['regiao']
            )
            session.merge(estado)  # merge para evitar duplicatas
        session.commit()
    print("Estados importados com sucesso")
def read_municipios(file_path):
    df = pd.read_csv(file_path)
    with Session() as session:
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
            session.merge(municipio)  # merge evita duplicatas
        session.commit()
    print("Municípios importados com sucesso")

def read_hospitais(file_path):
    df = check_file_type(file_path)
    with Session() as session:
        for _, row in df.iterrows():
            # Pega o municipio pelo código_ibge da cidade
            municipio = session.query(Municipio).filter_by(codigo_ibge=int(row['cidade'])).one_or_none()
            if municipio is None:
                print(f"Município com código {row['cidade']} não encontrado. Pulando hospital {row['nome']}")
                continue
            
            # Cria ou atualiza hospital
            hospital = session.query(Hospital).filter_by(codigo=row['codigo']).one_or_none()
            if hospital is None:
                hospital = Hospital(codigo=row['codigo'])
            
            hospital.nome = row['nome']
            hospital.municipio = municipio
            hospital.bairro = row.get('bairro', None)
            hospital.leitos_totais = int(row['leitos_totais']) if not pd.isna(row['leitos_totais']) else None

            # Limpa especialidades atuais
            hospital.especialidades.clear()
            
            # Associa especialidades (criando se necessário)
            especialidades_str = row.get('especialidades', '')
            for esp_nome in [e.strip() for e in especialidades_str.split(';') if e.strip()]:
                especialidade = session.query(Especialidade).filter_by(nome=esp_nome).one_or_none()
                if not especialidade:
                    especialidade = Especialidade(nome=esp_nome)
                    session.add(especialidade)
                    session.flush()  # para ter o id já
                hospital.especialidades.append(especialidade)

            session.merge(hospital)

        session.commit()
    print("Hospitais importados com sucesso!")

def read_especialidades(file_path):
    df = check_file_type(file_path)
    especialidades_set = set()

    # Extrai todas as especialidades do CSV
    for esp_str in df['especialidades'].dropna():
        esp_list = [e.strip() for e in esp_str.split(';')]
        especialidades_set.update(esp_list)

    with Session() as session:
        for esp_nome in especialidades_set:
            # Verifica se já existe para evitar duplicatas
            exists = session.query(Especialidade).filter_by(nome=esp_nome).first()
            if not exists:
                especialidade = Especialidade(nome=esp_nome)
                session.add(especialidade)
        session.commit()
    print(f"{len(especialidades_set)} especialidades inseridas/atualizadas com sucesso!")


def read_medicos(file_path):
    df = check_file_type(file_path)

    medicos = []

    with Session() as session:  # <-- aqui, sem engine!
        for _, row in df.iterrows():
            especialidade = session.query(Especialidade).filter_by(nome=row['especialidade']).first()
            if not especialidade:
                print(f"Especialidade '{row['especialidade']}' não encontrada para o médico '{row['nome_completo']}', pulando...")
                continue

            municipio = session.query(Municipio).filter_by(codigo_ibge=row['cidade']).first()
            if not municipio:
                print(f"Município '{row['cidade']}' não encontrado para o médico '{row['nome_completo']}', pulando...")
                continue

            try:
                codigo_uuid = uuid.UUID(row['codigo'])
            except (ValueError, TypeError):
                codigo_uuid = uuid.uuid4()

            medico = Medico(
                codigo=codigo_uuid,
                nome_completo=row['nome_completo'],
                especialidade_id=especialidade.id,
                municipio_id=municipio.codigo_ibge
            )
            medicos.append(medico)

        session.bulk_save_objects(medicos)
        session.commit()
    print(f"{len(medicos)} médicos inseridos com sucesso!")


BATCH_SIZE = 500

def processa_paciente(paciente_elem, session):
    # Processa o paciente a partir do XML
    codigo = paciente_elem.findtext("Codigo")
    cpf = paciente_elem.findtext("CPF")
    nome = paciente_elem.findtext("Nome_Completo")
    genero = paciente_elem.findtext("Genero")
    cod_municipio = paciente_elem.findtext("Cod_municipio")
    bairro = paciente_elem.findtext("Bairro")
    convenio = paciente_elem.findtext("Convenio")
    cid10_codigo = paciente_elem.findtext("CID-10").split(" ")[-1]

    # Buscar CID10
    cid10 = session.query(Cid10).filter_by(codigo=cid10_codigo).first()
    if not cid10:
        print(f"CID10 {cid10_codigo} não encontrado para paciente {nome}. Pulando...")
        return None

    # Converter código para UUID ou gerar novo caso inválido
    try:
        codigo_uuid = uuid.UUID(codigo)
    except (ValueError, TypeError):
        codigo_uuid = uuid.uuid4()

    paciente = Paciente(
        codigo=codigo_uuid,
        cpf=cpf,
        nome_completo=nome,
        genero=genero,
        municipio_id=cod_municipio,
        bairro=bairro,
        convenio=convenio,
        cid10_id=cid10.codigo
    )
    return paciente


def processa_pacientes_arquivo(file_path, session):
    contexto = ET.iterparse(file_path, events=("end",))
    pacientes_batch = []

    for evento, elem in contexto:
        if elem.tag == "Paciente":
            paciente = processa_paciente(elem, session)
            elem.clear()  # libera memória
            if paciente:
                pacientes_batch.append(paciente)

            if len(pacientes_batch) >= BATCH_SIZE:
                # Insere pacientes em batch ignorando duplicatas
                insert_pacientes_ignore_duplicates(pacientes_batch, session)
                pacientes_batch.clear()

    # Inserir os pacientes que restaram
    if pacientes_batch:
        insert_pacientes_ignore_duplicates(pacientes_batch, session)


def insert_pacientes_ignore_duplicates(pacientes_batch, session):
    # Coleta os dados para inserção em batch
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

    # Cria a query com INSERT IGNORE
    stmt = mysql_insert(Paciente).values(values).prefix_with("IGNORE")
    
    # Executa a query
    session.execute(stmt)
    session.commit()




if __name__ == "__main__":
    # read_cid10_file('sheet/tabela CID-10.xlsx', session)
    # read_estados('sheet/estados.csv')
    # read_municipios('sheet/municipios.csv')
    # read_especialidades('sheet/hospitais.csv')
    # read_hospitais('sheet/hospitais.csv')
    # read_medicos('sheet/medicos.csv')

    # processa_pacientes_arquivo('sheet/pacientes.xml', session)

    session.close()