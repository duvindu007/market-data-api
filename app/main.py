import logging
import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import DataBase
from app.api_routes import router
from app.logger import setup_logger


setup_logger() 

# create app
app = FastAPI()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")

    db = DataBase()
    db.initiate_tables()

    logger.info("Database initialized")

    yield   

    logger.info("Shutting down application...")


# create app with lifespan
app = FastAPI(lifespan=lifespan)

# include routes
app.include_router(router)


# run app
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )