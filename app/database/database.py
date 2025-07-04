from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///experiment_data.db"

# создаем движок, разрешаем соединения других потоков с БД
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# создаем фабрику сессий, запрещаем автоматические коммиты и сбросы
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# базовый класс для всех моделей
Base = declarative_base()

# функция для внедрения FastAPI-зависимости
def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()