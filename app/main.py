from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, UTC
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import get_db, SessionLocal
from app.models import Trigger, EventLog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts."""
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the scheduler when the application stops."""
    scheduler.shutdown()

class TriggerCreate(BaseModel):
    name: str
    type: str  # "scheduled" or "api"
    one_time_datetime: datetime | None = None
    payload: dict | None = None

class APITrigger(BaseModel):
    name: str
    payload: dict

@app.post("/triggers/")
async def create_trigger(trigger: TriggerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new trigger."""
    try:
        trigger_id = str(uuid.uuid4())
        new_trigger = Trigger(
            id=trigger_id,
            name=trigger.name,
            type=trigger.type,
            one_time_datetime=trigger.one_time_datetime,
            payload=trigger.payload,
            created_at=datetime.now(UTC)
        )
        db.add(new_trigger)
        await db.commit()

        logger.info(f"Successfully created trigger: {trigger_id}")

        if trigger.type == "scheduled" and trigger.one_time_datetime:
            scheduler.add_job(
                trigger_event,
                'date',
                run_date=trigger.one_time_datetime,
                args=[trigger_id]
            )
            logger.info(f"Scheduled job for trigger: {trigger_id}")

        return {"id": trigger_id, "message": "Trigger created successfully"}
    except Exception as e:
        logger.error(f"Error creating trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triggers/api/")
async def create_api_trigger(trigger: APITrigger, db: AsyncSession = Depends(get_db)):
    """Create and execute an API trigger immediately."""
    trigger_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())

    new_trigger = Trigger(
        id=trigger_id,
        name=trigger.name,
        type="api",
        payload=trigger.payload,
        created_at=datetime.now(UTC)
    )

    new_event = EventLog(
        id=event_id,
        trigger_id=trigger_id,
        name=trigger.name,
        type="api",
        executed_at=datetime.now(UTC),
        payload=trigger.payload,
        status="active"
    )

    db.add(new_trigger)
    db.add(new_event)
    await db.commit()

    return {"message": "API trigger executed", "trigger_id": trigger_id, "event_id": event_id}

@app.get("/triggers/")
async def list_triggers(db: AsyncSession = Depends(get_db)):
    """List all triggers."""
    result = await db.execute(select(Trigger))
    triggers = result.scalars().all()
    return {"triggers": [
        {
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "one_time_datetime": t.one_time_datetime,
            "payload": t.payload,
            "created_at": t.created_at
        } for t in triggers
    ]}

@app.get("/logs/")
async def list_logs(db: AsyncSession = Depends(get_db)):
    """List all event logs."""
    result = await db.execute(select(EventLog))
    logs = result.scalars().all()
    return {"logs": [
        {
            "id": log.id,
            "trigger_id": log.trigger_id,
            "name": log.name,
            "type": log.type,
            "executed_at": log.executed_at,
            "payload": log.payload,
            "status": log.status
        } for log in logs
    ]}

@app.get("/health/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check database connection."""
    try:
        result = await db.execute(text("SELECT 1"))
        await result.scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(UTC)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

async def trigger_event(trigger_id: str):
    """Function to execute when the trigger fires."""
    async with SessionLocal() as db:
        trigger = await db.get(Trigger, trigger_id)
        if trigger:
            event_id = str(uuid.uuid4())
            log_entry = EventLog(
                id=event_id,
                trigger_id=trigger_id,
                executed_at=datetime.now(UTC),
                payload=trigger.payload,
                status="completed"
            )
            db.add(log_entry)
            await db.commit()
            logger.info(f"Triggered event for {trigger.name} at {datetime.now(UTC)}")
