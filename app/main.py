from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database.init_db import init_db
from .file_handler import handler
from .endpoints import router
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # выполняется при старте
    init_db()
    asyncio.create_task(handler())
    yield
        

app = FastAPI(
    lifespan=lifespan,
    title="ExperimentData",
    description="API для работы с данными эксперимента",
    version="1.0.0"
)

app.include_router(router)