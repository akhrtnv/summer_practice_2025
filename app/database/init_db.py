from sqlalchemy import inspect
from .database import engine, Base

def init_db():
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    expected = {"files", "values", "results"}

    # пересоздание БД, если нет хотя бы одной таблицы
    if not expected.issubset(tables):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)