import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.database import DATABASE_URL

async def create_tables():
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Close the engine
    await engine.dispose()

# Run the async function
if __name__ == "__main__":
    asyncio.run(create_tables()) 