from sqlalchemy.orm import Session, joinedload
from ..database.models import File, Result
from fastapi import HTTPException, Depends
from ..database.database import get_db

class ResultService:
    def __init__(self, db: Session):
        self.db = db

    def get_results_by_filename(self, filename: str):
        file = (
            self.db.query(File)
            .filter(File.filename == filename)
            .options(joinedload(File.result))
            .first()
        )
        if not file:
            raise HTTPException(404, detail="Файл не найден")
        return [{"file": file, "result": file.result}]

    # * обязывает передавать все после нее по именованным аргументам
    # min_avg_value=...,
    def get_filtered_results(self, *, min_avg_value, max_avg_value, min_avg_duration, max_avg_duration):
        query = self.db.query(Result)

        if min_avg_value is not None:
            query = query.filter(Result.avg_value >= min_avg_value)
        if max_avg_value is not None:
            query = query.filter(Result.avg_value <= max_avg_value)
        if min_avg_duration is not None:
            query = query.filter(Result.avg_duration >= min_avg_duration)
        if max_avg_duration is not None:
            query = query.filter(Result.avg_duration <= max_avg_duration)

        results = query.options(joinedload(Result.file)).all()
        return [{"file": r.file, "result": r} for r in results]
    
    def get_service(db: Session = Depends(get_db)):
        return ResultService(db)