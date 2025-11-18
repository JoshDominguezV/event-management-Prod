from fastapi import APIRouter, HTTPException, Depends
import mysql.connector
from app.models.event_models import EventCreate, EventUpdate, EventResponse, EventAttendance
from app.database.connection import get_db

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("CreateEvent", (
        event.title, event.description, event.date,
        event.location, event.max_participants, event.organizer_id
    ))

    for result in cursor.stored_results():
        event_id = result.fetchone()["event_id"]

    db.commit()

    # Obtener evento creado
    cursor.callproc("GetEventById", (event_id,))
    for result in cursor.stored_results():
        event_data = result.fetchone()

    cursor.close()
    return EventResponse(**event_data)


@router.get("/upcoming")
async def get_upcoming_events(db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetUpcomingEvents")
    events = []
    for result in cursor.stored_results():
        events = result.fetchall()

    cursor.close()
    return {"events": events}


@router.get("/past")
async def get_past_events(db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetPastEvents")
    events = []
    for result in cursor.stored_results():
        events = result.fetchall()

    cursor.close()
    return {"events": events}


@router.get("/{event_id}")
async def get_event(event_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetEventById", (event_id,))
    for result in cursor.stored_results():
        event_data = result.fetchone()

    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")

    cursor.close()
    return EventResponse(**event_data)


@router.put("/{event_id}")
async def update_event(event_id: int, event_update: EventUpdate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("UpdateEvent", (
        event_id, event_update.title, event_update.description,
        event_update.date, event_update.location, event_update.max_participants
    ))

    db.commit()
    cursor.close()
    return {"message": "Event updated successfully"}


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("DeleteEvent", (event_id,))
    db.commit()
    cursor.close()
    return {"message": "Event deleted successfully"}


@router.post("/attend")
async def register_event_attendance(attendance: EventAttendance, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("RegisterAttendance", (attendance.user_id, attendance.event_id))
    db.commit()
    cursor.close()
    return {"message": "Attendance registered successfully"}


@router.get("/{event_id}/attendees")
async def get_event_attendees(event_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetEventAttendees", (event_id,))
    attendees = []
    for result in cursor.stored_results():
        attendees = result.fetchall()

    cursor.close()
    return {"attendees": attendees}