from fastapi import APIRouter, HTTPException, Depends
import mysql.connector
from app.models.social_models import CommentCreate, CommentResponse, ShareEvent
from app.database.connection import get_db

router = APIRouter(prefix="/social", tags=["Social Interaction"])


@router.post("/comments", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("CreateComment", (
        comment.user_id, comment.event_id, comment.content, comment.rating
    ))

    for result in cursor.stored_results():
        comment_id = result.fetchone()["comment_id"]

    db.commit()

    # Obtener comentario creado
    cursor.execute("""
        SELECT c.*, u.username, u.full_name 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.id = %s
    """, (comment_id,))
    comment_data = cursor.fetchone()

    cursor.close()
    return CommentResponse(**comment_data)


@router.get("/events/{event_id}/comments")
async def get_event_comments(event_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetEventComments", (event_id,))
    comments = []
    for result in cursor.stored_results():
        comments = result.fetchall()

    cursor.close()
    return {"comments": comments}


@router.post("/share")
async def share_event(share_data: ShareEvent, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("LogEventShare", (
        share_data.event_id, share_data.share_type, share_data.recipient
    ))

    db.commit()
    cursor.close()
    return {"message": "Event share logged successfully"}