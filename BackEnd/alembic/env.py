from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
import sqlalchemy
from alembic import context

# Importar a base dos seus modelos
from models import Base  # Ajuste conforme o nome do arquivo que contém a sua base de dados

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a URL de conexão do banco de dados
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_CONNECTION_STRING")

# Verificar se a URL do banco de dados foi carregada corretamente
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL não está definida no arquivo .env.")

# Este é o objeto de configuração do Alembic
config = context.config

# Configuração de log (não precisa ser alterada, a não ser que precise de ajuste)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aqui você define o metadata de seus modelos (isso é necessário para o autogenerate funcionar)
# Referencie o metadata da sua base de dados
target_metadata = Base.metadata  # Defina corretamente o metadata da sua base de modelos

# Definir a URL do banco de dados na configuração
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

def run_migrations_offline() -> None:
    """Executa migrações no modo offline.
    
    Isso configura o contexto apenas com a URL do banco, sem criar um Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa migrações no modo online.
    
    Neste caso, criamos um Engine e associamos a conexão com o contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Verificar se o modo offline ou online está ativado
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
