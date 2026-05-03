import logging
from fastapi import APIRouter, HTTPException
from app.market_service import MarketService
from app.exceptions import (
    DatabaseException,
    ExternalApiException,
    DataNotFoundException,
)


router = APIRouter()
market_service = MarketService()
logger = logging.getLogger(__name__)


@router.get("/get_annual_market_values/symbols/{symbol}/annual/{year}")
def get_all_markets(symbol:str, year:str):
    try:
        return market_service.get_annual_market_values(symbol_name= symbol,year=year) 
    
    except DataNotFoundException as error:
        raise HTTPException(status_code=404, detail=error.message)

    except ExternalApiException as error:
        raise HTTPException(status_code=502, detail=error.message)

    except DatabaseException as error:
        raise HTTPException(status_code=500, detail=error.message)

    except Exception:
        logger.exception("Unexpected error while getting annual market values")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/save_all/{symbol}")
def get_all_markets(symbol: str):
    try:
        logger.debug("Market save process started for symbol=%s", symbol)

        result = market_service.process_save_data(symbol_name=symbol)

        return {
            "message": "Market data saved successfully",
            "data": result
        }

    except DataNotFoundException as error:
        raise HTTPException(status_code=404, detail=error.message)

    except ExternalApiException as error:
        raise HTTPException(status_code=502, detail=error.message)

    except DatabaseException as error:
        raise HTTPException(status_code=500, detail=error.message)

    except Exception:
        logger.exception("Unexpected error while saving market data")
        raise HTTPException(status_code=500, detail="Internal server error")




