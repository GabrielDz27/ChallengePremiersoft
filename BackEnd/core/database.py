from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from core.configs import settings

# Engine assíncrono
engine: AsyncEngine = create_async_engine(settings.DB_URL)

# Factory de sessões
Session: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
