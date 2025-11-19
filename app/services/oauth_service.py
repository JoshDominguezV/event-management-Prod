import httpx
from fastapi import HTTPException
from app.database.connection import get_db
import mysql.connector
from config import settings


class OAuthService:

    @staticmethod
    async def verify_google_token(access_token: str, platform: str = "web"):
        """
        Verifica token de Google según la plataforma
        platform: 'web' o 'android'
        """

        print(f"🔐 Verificando token Google para plataforma: {platform}")

        # Verificar si es un token de prueba
        if access_token.startswith("test_google_"):
            from app.routes.oauth_simulator import TEST_TOKENS
            user_data = TEST_TOKENS["google"].get(access_token)
            if user_data:
                return {
                    "sub": user_data["provider_id"],
                    "email": user_data["email"],
                    "name": user_data["name"],
                    "given_name": user_data["name"].split()[0],
                    "family_name": user_data["name"].split()[-1],
                    "picture": None,
                    "email_verified": True
                }
            else:
                raise HTTPException(status_code=400, detail="Token de prueba inválido")

        # Para Android: Verificar token con Google API
        if platform == "android":
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Invalid Google access token")

                token_info = response.json()

                # Verificar que el token es para nuestra app Android
                if token_info.get("aud") != settings.GOOGLE_ANDROID_CLIENT_ID:
                    raise HTTPException(status_code=400, detail="Token not intended for this app")

                # Obtener información del usuario
                user_response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if user_response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to get user info")

                return user_response.json()

        # Para Web: Verificación normal
        else:
            async with httpx.AsyncClient() as client:
                print("🌐 Verificando token con Google API...")
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                print(f"📡 Respuesta de Google: {response.status_code}")

                if response.status_code != 200:
                    error_detail = f"Invalid Google access token: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_detail = f"Google API error: {error_data}"
                    except:
                        pass
                    raise HTTPException(status_code=400, detail=error_detail)

                user_info = response.json()
                print(f"✅ Usuario verificado: {user_info.get('email')}")
                return user_info

    @staticmethod
    async def get_facebook_user_info(access_token: str):
        """Obtiene información del usuario de Facebook"""
        print(f"🔐 Verificando token Facebook...")

        # Verificar si es un token de prueba
        if access_token.startswith("test_facebook_"):
            from app.routes.oauth_simulator import TEST_TOKENS
            user_data = TEST_TOKENS["facebook"].get(access_token)
            if user_data:
                return {
                    "id": user_data["provider_id"],
                    "name": user_data["name"],
                    "email": user_data["email"]
                }
            else:
                raise HTTPException(status_code=400, detail="Token de prueba inválido")

        # Flujo real con Facebook API
        async with httpx.AsyncClient() as client:
            print("🌐 Verificando token con Facebook API...")
            response = await client.get(
                f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
            )

            print(f"📡 Respuesta de Facebook: {response.status_code}")

            if response.status_code != 200:
                error_detail = f"Invalid Facebook access token: {response.status_code}"
                try:
                    error_data = response.json()
                    error_detail = f"Facebook API error: {error_data}"
                except:
                    pass
                raise HTTPException(status_code=400, detail=error_detail)

            user_info = response.json()
            print(f"✅ Usuario Facebook: {user_info.get('name')}")
            return user_info

    @staticmethod
    def find_or_create_user_from_oauth(provider: str, provider_id: str, email: str, name: str, role: str, db):
        """Busca o crea un usuario desde OAuth"""
        cursor = db.cursor(dictionary=True)

        try:
            print(f"👤 Buscando/creando usuario: {email}")

            # Buscar si ya existe autenticación social
            cursor.execute(
                "SELECT user_id FROM social_auth WHERE provider = %s AND provider_id = %s",
                (provider, provider_id)
            )
            existing_auth = cursor.fetchone()

            if existing_auth:
                user_id = existing_auth["user_id"]
                print(f"✅ Usuario existente encontrado: {user_id}")
            else:
                # Buscar usuario por email
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    user_id = existing_user["id"]
                    print(f"✅ Usuario por email encontrado: {user_id}")
                else:
                    # Crear nuevo usuario
                    username = email.split('@')[0]
                    # Asegurar que el username sea único
                    base_username = username
                    counter = 1
                    while True:
                        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                        if not cursor.fetchone():
                            break
                        username = f"{base_username}{counter}"
                        counter += 1

                    print(f"🆕 Creando nuevo usuario: {username}")
                    cursor.execute(
                        "INSERT INTO users (username, email, full_name, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                        (username, email, name, "oauth_password", role)
                    )
                    user_id = cursor.lastrowid
                    print(f"✅ Nuevo usuario creado: {user_id}")

                # Crear registro de autenticación social
                cursor.execute(
                    "INSERT INTO social_auth (user_id, provider, provider_id) VALUES (%s, %s, %s)",
                    (user_id, provider, provider_id)
                )
                print(f"🔗 Autenticación social creada para: {provider}")

            db.commit()
            return user_id

        except mysql.connector.Error as e:
            db.rollback()
            print(f"❌ Error de base de datos: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            cursor.close()