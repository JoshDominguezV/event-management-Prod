from fastapi import APIRouter, HTTPException, Depends, Body
from app.services.oauth_service import OAuthService
from app.database.connection import get_db
import mysql.connector
from app.models.user_models import UserRole

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.post("/google")
async def oauth_google(
        access_token: str = Body(..., embed=True),
        role: UserRole = Body(UserRole.PARTICIPANT, embed=True),
        platform: str = Body("web", embed=True),
        db: mysql.connector.MySQLConnection = Depends(get_db)
):
    try:
        print(f"🔐 Procesando OAuth Google con token: {access_token[:20]}...")

        # Obtener información del usuario de Google
        user_info = await OAuthService.verify_google_token(access_token, platform)

        print(f"✅ Usuario de Google: {user_info['email']}")

        # Buscar o crear usuario
        user_id = OAuthService.find_or_create_user_from_oauth(
            provider="google",
            provider_id=user_info["sub"],
            email=user_info["email"],
            name=user_info["name"],
            role=role.value,
            db=db
        )

        return {
            "message": "Google OAuth successful",
            "user_id": user_id,
            "email": user_info["email"],
            "name": user_info["name"],
            "role": role.value,
            "platform": platform
        }

    except Exception as e:
        print(f"❌ Error en OAuth Google: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/facebook")
async def oauth_facebook(
        access_token: str = Body(..., embed=True),
        role: UserRole = Body(UserRole.PARTICIPANT, embed=True),
        db: mysql.connector.MySQLConnection = Depends(get_db)
):
    try:
        print(f"🔐 Procesando OAuth Facebook con token: {access_token[:20]}...")

        # Obtener información del usuario de Facebook
        user_info = await OAuthService.get_facebook_user_info(access_token)

        print(f"✅ Usuario de Facebook: {user_info.get('email', 'no-email')}")

        # Buscar o crear usuario
        user_id = OAuthService.find_or_create_user_from_oauth(
            provider="facebook",
            provider_id=user_info["id"],
            email=user_info.get("email", f"{user_info['id']}@facebook.com"),
            name=user_info["name"],
            role=role.value,
            db=db
        )

        return {
            "message": "Facebook OAuth successful",
            "user_id": user_id,
            "email": user_info.get("email"),
            "name": user_info["name"],
            "role": role.value
        }

    except Exception as e:
        print(f"❌ Error en OAuth Facebook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))