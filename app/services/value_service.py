from sqlalchemy.orm import Session, joinedload
from ..database.models import File
from fastapi import HTTPException, Depends
from ..database.dep import get_db

class ValueService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_values_by_filename(self, filename: str):
        file = (
            self.db.query(File)
            .filter(File.filename == filename)
            .options(joinedload(File.values))
            .first()
        )
        if not file:
            raise HTTPException(404, detail="Файл не найден")
        return {"file": file, "values": file.values}
    
    def get_service(db: Session = Depends(get_db)):
        return ValueService(db)
