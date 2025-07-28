import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .base import Base

# Database URL with environment variable support for GCP
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/mydb"
)

# For GCP Cloud SQL, you might need a URL like:
# DATABASE_URL = "postgresql+asyncpg://username:password@/database?host=/cloudsql/project:region:instance"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()