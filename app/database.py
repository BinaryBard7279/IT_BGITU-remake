from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.performance import setup_db_profiling

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, # echo должен быть False, чтобы наш логгер работал чисто
    pool_size=20,
    max_overflow=10
)

setup_db_profiling(engine)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
