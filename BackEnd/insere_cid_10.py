import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Cid10, Base  # importe seu model Cid10 aqui

# Configurar conexão com MySQL (ajuste a senha e banco)
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/data_saude')
Session = sessionmaker(bind=engine)
session = Session()

# Ler XLSX pulando as 2 primeiras linhas (header na linha 3)
df = pd.read_excel('seu_arquivo.xlsx', skiprows=2, header=None, names=['raw'])

# Lista para guardar os objetos Cid10
cid10_list = []

for raw_text in df['raw']:
    if pd.isna(raw_text):
        continue  # pula linhas vazias

    # Se contém ':', é linha de capítulo, pega o texto depois dos dois pontos
    if ':' in raw_text:
        descricao = raw_text.split(':', 1)[1].strip()
        # Usar código 'Capítulo' + descrição simplificada, ou pode optar por não inserir no banco
        # Vou criar um código genérico para capítulo, ex: CAP1, CAP2...
        # Se quiser ignorar capítulos, pule essa parte
        codigo = 'CAP' + descricao.split()[0]  # exemplo: 'CAPI' para 'I'
        cid10_list.append(Cid10(codigo=codigo, descricao=descricao))
    else:
        # linha com padrão {ID} - {Descrição}
        if ' - ' in raw_text:
            codigo, descricao = raw_text.split(' - ', 1)
            codigo = codigo.strip()
            descricao = descricao.strip()
            cid10_list.append(Cid10(codigo=codigo, descricao=descricao))
        else:
            # linha que não bate com padrão esperado, ignorar ou logar
            print(f"Ignorado: {raw_text}")

# Inserir no banco
session.bulk_save_objects(cid10_list)
session.commit()
print(f"{len(cid10_list)} registros inseridos com sucesso!")
