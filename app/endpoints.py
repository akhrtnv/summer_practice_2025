from fastapi import (
    APIRouter, UploadFile, Form, HTTPException, Query, Depends
)
from fastapi import File as fFile
from .file_handler import file_queue
from typing import List, Optional
from .schemas import ResultResponse, ValuesResponse
from .database.database import get_db
from .database.models import File, Value, Result
from sqlalchemy.orm import Session, joinedload
import aiofiles
import uuid

router = APIRouter()

@router.post("/science/files/")
async def post_file(
    file: UploadFile = fFile(...), 
    author: str = Form(...)
):
    # проверка формата файла
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Ожидался файл с расширением .csv"
        )

    filepath = f"./tmp/{uuid.uuid4()}.csv"
    
    async with aiofiles.open(filepath, "wb") as out_file:  # открываем файл для записи
        while chunk := await file.read(1024):              # считываем из полученного файла фрагмент
            await out_file.write(chunk)                    # записываем

    await file_queue.put((file.filename, filepath, author))  # добавляем в очередь обработки
    await file.close()
    return {"message": "Файл принят для обработки"}

@router.get("/science/results/", response_model=List[ResultResponse])
def get_results(
    filename:         Optional[str] = Query(None, alias="fileName"),
    min_avg_value:    Optional[float] = Query(None, alias="minAvgValue"),
    max_avg_value:    Optional[float] = Query(None, alias="maxAvgValue"),
    min_avg_duration: Optional[int] = Query(None, alias="minAvgDuration"),
    max_avg_duration: Optional[int] = Query(None, alias="maxAvgDuration"),
    db: Session = Depends(get_db)  # сессия с БД
):
    if filename:
        file = ( 
            db.query(File)
            .filter(File.filename == filename)
            .options(joinedload(File.result))  # подгружаем связанные данные из таблицы результатов
            .first()
        )
        if not file:
            raise HTTPException(404, detail="Файл не найден")
        
        return [{"file": file, "result": file.result}]
    
    query = db.query(Result)

    if min_avg_value:
        query = query.filter(Result.avg_value >= min_avg_value)
    
    if max_avg_value:
        query = query.filter(Result.avg_value <= max_avg_value)
    
    if min_avg_duration:
        query = query.filter(Result.avg_duration >= min_avg_duration)
    
    if max_avg_duration:
        query = query.filter(Result.avg_duration <= max_avg_duration)
    
    results = query.options(joinedload(Result.file)).all()
    
    return [{"file": result.file, "result": result} for result in results]

@router.get("/science/values/{fileName}", response_model=ValuesResponse)
def get_values(fileName: str, db: Session = Depends(get_db)):
    file = (
        db.query(File)
        .filter(File.filename == fileName)
        .options(joinedload(File.values))
        .first()
    )

    if not file:
        raise HTTPException(404, detail="Файл не найден")

    return {"file": file, "values": file.values}