from fastapi import APIRouter, Depends
import mysql.connector
from app.database.connection import get_db

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/user/{user_id}")
async def get_user_stats(user_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetUserEventStats", (user_id,))
    for result in cursor.stored_results():
        stats = result.fetchone()

    cursor.close()
    return {"user_id": user_id, "statistics": stats}


@router.get("/event/{event_id}")
async def get_event_stats(event_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetEventStatistics", (event_id,))
    for result in cursor.stored_results():
        stats = result.fetchone()

    cursor.close()
    return {"event_id": event_id, "statistics": stats}