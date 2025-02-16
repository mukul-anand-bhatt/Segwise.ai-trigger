# FastAPI Trigger and Event Logger

## Overview

This FastAPI application manages triggers and logs events based on those triggers. It supports both scheduled and API-based triggers, using **APScheduler** for scheduling and **SQLAlchemy** with PostgreSQL for data persistence.

## Features

- Create scheduled triggers that execute at a specified time.
- Create API-based triggers that execute immediately.
- List all triggers.
- List all event logs.
- Health check endpoint to verify database connection.

## Technologies Used

- **FastAPI** (Web framework)
- **APScheduler** (Task scheduling)
- **SQLAlchemy** (Database ORM)
- **PostgreSQL** (Database)
- **Async SQLAlchemy** (Async database interactions)

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL database
- `pip` for package management

### Installation Steps

1. **Clone the repository**

   ```sh
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables** Create a `.env` file in the project root with the following content:

   ```ini
   DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
   ```

5. **Run database migrations**

   ```sh
   python -m app.database
   ```

6. **Start the FastAPI application**

   ```sh
   uvicorn app.main:app --reload
   ```

## API Endpoints

### **Trigger Endpoints**

#### 1. Create a Scheduled Trigger

```http
POST /triggers/
```

**Request Body:**

```json
{
  "name": "Daily Report",
  "type": "scheduled",
  "one_time_datetime": "2025-02-17T10:00:00",
  "payload": {"message": "Generate Report"}
}
```

**Response:**

```json
{
  "id": "uuid",
  "message": "Trigger created successfully"
}
```

#### 2. Create an API Trigger (Executes Immediately)

```http
POST /triggers/api/
```

**Request Body:**

```json
{
  "name": "Immediate Execution",
  "payload": {"action": "send_email"}
}
```

**Response:**

```json
{
  "message": "API trigger executed",
  "trigger_id": "uuid",
  "event_id": "uuid"
}
```

#### 3. List All Triggers

```http
GET /triggers/
```

**Response:**

```json
{
  "triggers": [
    {
      "id": "uuid",
      "name": "Daily Report",
      "type": "scheduled",
      "one_time_datetime": "2025-02-17T10:00:00",
      "payload": {"message": "Generate Report"},
      "created_at": "2025-02-16T10:00:00"
    }
  ]
}
```

### **Event Log Endpoints**

#### 4. List All Logs

```http
GET /logs/
```

**Response:**

```json
{
  "logs": [
    {
      "id": "uuid",
      "trigger_id": "uuid",
      "name": "Daily Report",
      "type": "scheduled",
      "executed_at": "2025-02-17T10:00:00",
      "payload": {"message": "Generate Report"},
      "status": "completed"
    }
  ]
}
```

### **Health Check Endpoint**

#### 5. Check Database Connection

```http
GET /health/
```

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-02-16T12:00:00"
}
```


