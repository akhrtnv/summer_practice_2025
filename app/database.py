from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///experiment_data.db"

# создаем движок, разрешаем соединения других потоков с БД
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# создаем фабрику сессий, запрещаем автоматические коммиты и сбросы
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# базовый класс для всех моделей
Base = declarative_base()

# TODO: поэксперементируй с каскадом