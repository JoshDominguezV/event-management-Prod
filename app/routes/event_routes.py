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

    try:
        # Obtener evento original para detectar cambios
        cursor.callproc("GetEventById", (event_id,))
        original_event = None
        for result in cursor.stored_results():
            original_event = result.fetchone()

        if not original_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Detectar cambios importantes
        changes_detected = {
            "date_changed": False,
            "location_changed": False,
            "changes": []
        }

        if event_update.date and event_update.date != original_event['date']:
            changes_detected["date_changed"] = True
            changes_detected["changes"].append(f"Fecha: {original_event['date']} → {event_update.date}")

        if event_update.location and event_update.location != original_event['location']:
            changes_detected["location_changed"] = True
            changes_detected["changes"].append(f"Ubicación: {original_event['location']} → {event_update.location}")

        # Actualizar evento
        cursor.callproc("UpdateEvent", (
            event_id, event_update.title, event_update.description,
            event_update.date, event_update.location, event_update.max_participants
        ))

        db.commit()

        # Si hubo cambios, obtener lista de usuarios afectados
        affected_users = []
        if changes_detected["date_changed"] or changes_detected["location_changed"]:
            cursor.callproc("GetEventAttendees", (event_id,))
            for result in cursor.stored_results():
                attendees = result.fetchall()
                affected_users = [{"user_id": a["id"], "username": a["username"], "email": a.get("email")} for a in attendees]

        cursor.close()

        response = {
            "message": "Event updated successfully",
            "changes_detected": len(changes_detected["changes"]) > 0,
            "details": changes_detected["changes"]
        }

        if affected_users:
            response["affected_users_count"] = len(affected_users)
            response["notification_message"] = f"IMPORTANTE: El evento '{original_event['title']}' ha sido modificado. Cambios: {'; '.join(changes_detected['changes'])}"

        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()

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