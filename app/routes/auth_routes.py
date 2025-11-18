from fastapi import APIRouter, HTTPException, Depends
import mysql.connector
from app.models.user_models import UserCreate, UserLogin, UserResponse, SocialAuth
from app.utils.security import hash_password, verify_password
from app.database.connection import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    # Verificar si el usuario ya existe
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s",
                   (user.username, user.email))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Crear usuario
    hashed_password = hash_password(user.password)
    cursor.callproc("CreateUser", (user.username, user.email, user.full_name, hashed_password))

    for result in cursor.stored_results():
        user_id = result.fetchone()["user_id"]

    db.commit()

    # Obtener usuario creado
    cursor.callproc("GetUserById", (user_id,))
    for result in cursor.stored_results():
        user_data = result.fetchone()

    cursor.close()
    return UserResponse(**user_data)


@router.post("/login")
async def login_user(login_data: UserLogin, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    cursor.callproc("GetUserByUsername", (login_data.username,))
    for result in cursor.stored_results():
        user_data = result.fetchone()

    if not user_data or not verify_password(login_data.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    cursor.close()
    return {"message": "Login successful", "user_id": user_data["id"]}


@router.post("/social-auth")
async def social_auth(social_data: SocialAuth, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)

    # Verificar si ya existe autenticación social
    cursor.execute("SELECT user_id FROM social_auth WHERE provider = %s AND provider_id = %s",
                   (social_data.provider, social_data.provider_id))
    existing_auth = cursor.fetchone()

    if existing_auth:
        user_id = existing_auth["user_id"]
    else:
        # Crear nuevo usuario o vincular con existente
        cursor.execute("SELECT id FROM users WHERE email = %s", (social_data.email,))
        existing_user = cursor.fetchone()

        if existing_user:
            user_id = existing_user["id"]
        else:
            # Crear nuevo usuario
            username = social_data.email.split('@')[0]
            cursor.callproc("CreateUser", (username, social_data.email, social_data.full_name, ""))
            for result in cursor.stored_results():
                user_id = result.fetchone()["user_id"]

        # Vincular autenticación social
        cursor.execute("INSERT INTO social_auth (user_id, provider, provider_id) VALUES (%s, %s, %s)",
                       (user_id, social_data.provider, social_data.provider_id))

    db.commit()
    cursor.close()
    return {"message": "Social authentication successful", "user_id": user_id}