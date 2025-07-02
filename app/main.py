from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database.init_db import init_db
from .database import database
from .services.file_queue import file_queue
from .services.file_handler import FileHandler
from .endpoints import router
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # выполняется при старте
    init_db()
    handler = FileHandler(database.session_factory)
    asyncio.create_task(handler.run_handler(file_queue))
    
    yield

app = FastAPI(
    lifespan=lifespan,
    title="ExperimentData",
    description="API для работы с данными эксперимента",
    version="1.0.0"
)

app.include_router(router)