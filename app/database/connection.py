import mysql.connector
from mysql.connector import Error
from config import settings


class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host="postgresql://root:G5TWKXVdoy2HI1KxWCnEQY6lNPVz7tR4@dpg-d4h49humcj7s73bq3b3g-a/event_management_8fim",
                user="root",
                password="",
                database="event_management"
            )
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()


def get_db():
    db = DatabaseConnection()
    connection = db.get_connection()
    try:
        yield connection
    finally:
        db.close_connection()