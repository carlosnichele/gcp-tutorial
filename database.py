from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # SOLO per uso locale / script: incolla qui la stringa di Railway
    DATABASE_URL = "postgresql://postgres:CIMxXuKnFsjpNowHCWcxYxqyWPSiCKIK@postgres.railway.internal:5432/railway"

# Railway usa "postgresql://" ma SQLAlchemy async richiede "postgresql+asyncpg://"
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
