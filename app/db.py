import sqlite3
from app.config import DB_NAME

class DataBase:
    def __init__(self, db_name = DB_NAME):
        self.db_name = db_name

    def get_connection(self):
               conn = sqlite3.connect(self.db_name)
               conn.execute("PRAGMA foreign_keys = ON")
               return conn
    
    def initiate_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_name TEXT
            )
        """)


        cursor.execute("""  
                CREATE TABLE IF NOT EXISTS  TIME_SERIES_MONTHLY (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       symbol_id INTEGER,
                       high REAL,
                        low REAL,
                        volume REAL,
                        month TEXT,
                        year TEXT,
                        FOREIGN KEY (symbol_id) REFERENCES job_types(id)
                       )
        """
                         )
        conn.commit()
        conn.close()
