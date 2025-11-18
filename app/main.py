from fastapi import FastAPI
from app.routes import auth_routes, event_routes, social_routes, stats_routes
from app.database.connection import DatabaseConnection

app = FastAPI(
    title="Event Management API",
    description="Sistema de gestión de eventos con autenticación e interacción social",
    version="1.0.0"
)

# Incluir rutas
app.include_router(auth_routes.router)
app.include_router(event_routes.router)
app.include_router(social_routes.router)
app.include_router(stats_routes.router)

@app.get("/")
async def root():
    return {"message": "Event Management API is running"}

@app.on_event("startup")
async def startup_event():
    # Verificar conexión a la base de datos
    db = DatabaseConnection()
    connection = db.get_connection()
    if connection:
        print("✅ Database connection established")
        db.close_connection()
    else:
        print("❌ Failed to connect to database")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)