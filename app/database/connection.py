import mysql.connector
from mysql.connector import Error
from config import settings


class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
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