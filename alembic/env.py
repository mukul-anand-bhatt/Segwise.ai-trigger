from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Import your models
from app.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configure Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Logging setup
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata  # 🔹 This ensures Alembic knows about your tables

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode with async engine."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(context.configure, connection=connection, target_metadata=target_metadata)
        await connection.run_sync(context.run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
