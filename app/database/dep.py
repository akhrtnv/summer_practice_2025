from .database import session_factory

# функция внедрения зависимости
def get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()