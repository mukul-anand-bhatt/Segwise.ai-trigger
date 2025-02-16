import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Correctly formatted DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Ensure asyncpg is used
if "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Simple async DB connection test
async def async_main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 'hello world'"))
        print(result.fetchall())
    await engine.dispose()

# Run DB connection test only when executing the script directly
if __name__ == "__main__":
    asyncio.run(async_main())
