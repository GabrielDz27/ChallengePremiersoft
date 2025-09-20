
from sqlmodel import SQLModel
from core.database import engine

async def create_tables() -> None:
    import models.__all__models
    print("Criando as tabelas no Banco de Dados")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

        print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())