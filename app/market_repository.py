import sqlite3
import logging

from app.db import DataBase
from app.model import Market, Symbols, MarketResponse
from app.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class MarketRepository:
    def __init__(self):
        self.db = DataBase()

    def get_connection(self):
        return self.db.get_connection()

    def save_montly_market_data(self, cursor, monthly: Market):
        #  Insert a single monthly record into DB
        try:
            cursor.execute(""" 
                           INSERT OR IGNORE INTO TIME_SERIES_MONTHLY(symbol_id, high, low, volume, month, year)
                            VALUES (?,?,?,?,?,?)
                            """,
                           (monthly.symbol_id, monthly.high, monthly.low, monthly.volume, monthly.month, monthly.year,))
            return cursor.rowcount
        except sqlite3.Error as error:
            logger.exception("Failed to save monthly market data")
            raise DatabaseException(f"Database insert error: {error}")

    def bulk_save_monthly_market_data(self, cursor, monthly_data: list[Market]):
        #Bulk insert multiple records
        try:
            rows = [
                (
                    item.symbol_id,
                    item.high,
                    item.low,
                    item.volume,
                    item.month,
                    item.year
                )
                for item in monthly_data
            ]

            cursor.executemany("""
                INSERT OR IGNORE INTO TIME_SERIES_MONTHLY
                (symbol_id, high, low, volume, month, year)
                VALUES (?, ?, ?, ?, ?, ?)
            """, rows)

            return cursor.rowcount

        except sqlite3.Error as error:
            logger.exception("Failed to bulk save monthly market data")
            raise DatabaseException(f"Database bulk insert error: {error}")    


    def get_existing_months(self,cursor, symbol_id):
        #get year, month pairs already stored for a symbol
        try:
            cursor.execute("""
                            SELECT year, month 
                            FROM TIME_SERIES_MONTHLY
                            WHERE symbol_id = ?   
                                """, (symbol_id,))
            return {(row[0], row[1]) for row in cursor.fetchall()}
        
        except sqlite3.Error as error:
            logger.exception("Failed to get existing months")
            raise DatabaseException(f"Database select error: {error}")


    def check_year_symbol(self, cursor, symbol_id: int, year: str):
        # Count how many records exist for a symbol in a given year
        try:
            cursor.execute("""
                       SELECT COUNT(1) 
                       FROM TIME_SERIES_MONTHLY tsm
                       WHERE tsm.symbol_id= ? and tsm.year = ?
                       """, (symbol_id, year))
            return int(cursor.fetchone()[0])

        except sqlite3.Error as error:
            logger.exception("Failed to check year symbol count")
            raise DatabaseException(f"Database count error: {error}")



    def find_symbol_year_market_data(self, cursor, symbol_id: int, year: str):
         #Aggregate yearly data:- MIN(low), - MAX(high), - SUM(volume)

        try:
            cursor.execute(""" 
                            SELECT MIN(tsm.low) , MAX(tsm.high), SUM(tsm.volume) 
                            FROM TIME_SERIES_MONTHLY tsm WHERE tsm.symbol_id=? and tsm.year = ?
                            """, (symbol_id, year))
            row = cursor.fetchone()
            
            if not row:
                return None 
            
            return MarketResponse(low=row[0] or 0, high=row[1] or 0, volume=row[2] or 0)
            
        except sqlite3.Error as error:
            logger.exception("Failed to find annual market data")
            raise DatabaseException(f"Database select error: {error}")
    

    def get_symobol_details_by_id(self,cursor, symmbol_id: int):
        #get symbol details using primary key
       
        try:
            cursor.execute(""" 
                                SELECT s.id, s.symbol_name  FROM SYMBOLS s where s.id = ?
                                    """, (symmbol_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Symbols(id=row[0], symbol_name=row[1])
        
        except sqlite3.Error as error:
            logger.exception("Failed to get symbol by id")
            raise DatabaseException(f"Database select error: {error}")

    def get_symobol_details_by_symbol_name(self,cursor, symbol_name: str):
         # get symbol using symbol name 
        try:
            cursor.execute(""" 
                                SELECT s.id, s.symbol_name  FROM SYMBOLS s where s.symbol_name = ?
                                    """, (symbol_name,))
            row = cursor.fetchone()

            if not row:
                return None
            return Symbols(id=row[0], symbol_name=row[1])
        
        except sqlite3.Error as error:
            logger.exception("Failed to get symbol by name")
            raise DatabaseException(f"Database select error: {error}")


    def get_or_create_symbol(self,cursor, symbol_name):
        #  Try to fetch symbol first, If not exists → insert new symbol
        try: 
            cursor.execute("SELECT id, symbol_name from symbols WHERE symbol_name = ?", (symbol_name,))
            row1 = cursor.fetchone()
            if row1:
                return Symbols(id=row1[0], symbol_name=row1[1])
            
            cursor.execute("INSERT INTO symbols (symbol_name) VALUES (?) RETURNING id, symbol_name", (symbol_name,))

            row2 = cursor.fetchone()
            return Symbols(id=row2[0], symbol_name=row2[1])
        
        except sqlite3.Error as error:
            logger.exception("Failed to get or create symbol")
            raise DatabaseException(f"Database symbol insert error: {error}")

