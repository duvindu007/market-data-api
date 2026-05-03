import logging
from app.market_repository import MarketRepository
from app.external_api import ExternalApiClient
from datetime import datetime
from app.model import Market, MarketResponse, Symbols
from app.exceptions import (
    ExternalApiException,
    DataNotFoundException,
    MarketDataNotFoundException
)

logger = logging.getLogger(__name__)


class MarketService:
    def __init__(self):
        self.repository = MarketRepository()
        self.external_api = ExternalApiClient()

    def process_save_data(self,symbol_name: str):
        conn = self.repository.get_connection()
        
        try:
            cursor= conn.cursor()
            #get and transform API data into Market objects
            results = self.get_monthly_data_api(symbol_name=symbol_name, cursor=cursor)

            # Bulk insert all records
            inserted = self.repository.bulk_save_monthly_market_data(cursor=cursor, monthly_data=results)

            conn.commit()

            return {
            "symbol": symbol_name,
            "inserted": inserted
             }
        except Exception:
        # Rollback on failure to maintain DB consistency
            conn.rollback()
            logger.exception("Failed to process save data")
            raise
        finally:
            conn.close()


    def save_all_market_data(self, montly_data: list[MarketResponse], monthly_markets: list[dict]):
        for data in montly_data:
            self.repository.get_or_create_symbol(Market)

        for monthly_market in monthly_markets:
            self.repository.save_montly_market_data(monthly_market)

    def get_annual_market_values(self, symbol_name: str, year: str):
        # get aggregated yearly market data
        # ensures all full 12 month data exists
        conn = self.repository.get_connection()

        try:
            cursor = conn.cursor()
            # check if symbol exists
            symbol = self.repository.get_or_create_symbol(cursor=cursor, symbol_name=symbol_name)

            # check how many month are stored for this year
            count = self.repository.check_year_symbol(cursor=cursor,symbol_id=symbol.id, year=year)

            if count < 12:
                new_records = self.update_market_data(symbol_value=symbol, conn=conn, cursor=cursor)

            result = self.repository.find_symbol_year_market_data(cursor=cursor,symbol_id=symbol.id, year=year)

            if result is None:
                raise DataNotFoundException("Market data not found")
            
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            logger.exception("Failed to get annual market values")
            raise
        finally:
            conn.close()



    def update_market_data(self, symbol_value : Symbols,conn=None, cursor=None ):
         # Determine if this method owns the DB connection
         # If conn/cursor are not provided → this method must create/manage them
        open_connection = conn is None or cursor is None

        if open_connection:
            conn = self.repository.get_connection()
            cursor = conn.cursor()

        try:
            #Call external API and transform data into Market objects
            results = self.get_monthly_data_api(symbol_name=symbol_value.symbol_name, cursor=cursor)
            #Get already existing (year, month) from DB to avoid duplicates
            existing_months = self.repository.get_existing_months(cursor=cursor , symbol_id= symbol_value.id)

            #Filter only missing records that is not in the db
            records_new = [result for result in results 
                           if (result.year, result.month) not in existing_months]
            
            # Bulk insert new records
            inserted = self.repository.bulk_save_monthly_market_data(cursor=cursor, monthly_data= records_new)

            if open_connection:
                conn.commit()
            return inserted

        except Exception:
        #Rollback only if this method owns the transaction
            if open_connection:
                conn.rollback()
                logger.exception("Failed to update market data")
                raise

        finally:
            # Close connection only if created here
             if open_connection:
                conn.close()
    



    def get_symbol(self, symbol_id: int | None, symbol_name: str | None):
        # get symbol details by id or name
        conn = self.repository.get_connection()
        try:
            cursor = conn.cursor()

            if symbol_id is not None:
                return self.repository.get_symobol_details_by_id(cursor=cursor,symmbol_id=symbol_id)
            
            if symbol_name is not None:
                return self.repository.get_symobol_details_by_symbol_name(cursor=cursor, symbol_name=symbol_name)
            
            #if invalid or no input invalid request
            raise DataNotFoundException("Symbol id or symbol name is required")
        
        except Exception:
            logger.exception("Failed to get symbol")
            raise
        finally:
            conn.close()

    def get_monthly_data_api(self, symbol_name:str, cursor):
        # calls external api and converts response into Market objects
        try:     

            api_data = self.external_api.fetch_market_data(symbol=symbol_name)

            if "Meta Data" not in api_data:
                raise ExternalApiException("Meta Data missing in API response") 
            
            if "Monthly Time Series" not in api_data:
                raise ExternalApiException("Monthly Time Series missing in API response")

            symbol_value = api_data["Meta Data"]["2. Symbol"]
            monthly_data = api_data["Monthly Time Series"]

            if not monthly_data:
                raise MarketDataNotFoundException("Monthly market data not found")
            
            symbol = self.repository.get_or_create_symbol(cursor=cursor, symbol_name=symbol_value)

            results = []

            for date, values in monthly_data.items():
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                results.append(Market(symbol_id=symbol.id, high=values["2. high"], low=values["3. low"],
                                  volume=values["5. volume"], month=date_obj.strftime("%B"), year=str(date_obj.year)))

            return results
        
        except KeyError as error:
            raise ExternalApiException(f"Missing API field: {error}") from error

        except ValueError as error:
            raise ExternalApiException(f"Invalid API data format: {error}") from error
