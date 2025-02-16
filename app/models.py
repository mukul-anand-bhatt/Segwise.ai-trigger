from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Async DB Engine & Session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# Trigger Model
class Trigger(Base):
    __tablename__ = "triggers"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "scheduled" or "api"
    one_time_datetime = Column(DateTime, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

# Event Log Model
class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(String, primary_key=True)
    trigger_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    executed_at = Column(DateTime, default=lambda: datetime.now(UTC))
    payload = Column(JSON, nullable=True)
    status = Column(String, default="active")  # "active", "archived"
