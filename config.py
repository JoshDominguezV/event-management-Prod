import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:password@localhost/event_management")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

    # OAuth Configurations
    GOOGLE_WEB_CLIENT_ID = os.getenv("GOOGLE_WEB_CLIENT_ID", "1035754646955-hcemevori7oujj3rliv96revn52c0bt7.apps.googleusercontent.com")
    GOOGLE_WEB_CLIENT_SECRET = os.getenv("GOOGLE_WEB_CLIENT_SECRET", "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")

    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET", "")


settings = Settings()