import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:password@localhost/event_management")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

settings = Settings()