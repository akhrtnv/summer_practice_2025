from fastapi import FastAPI
from contextlib import asynccontextmanager
from app import file_handler, init_db, endpoints
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # выполняется при старте
    init_db.init_db()
    asyncio.create_task(file_handler.handler())
    yield
    # выполняется при завершении

app = FastAPI(
    lifespan=lifespan,
    # title="",
    # description="",
    version="1.0.0"
)

app.include_router(endpoints.router)
