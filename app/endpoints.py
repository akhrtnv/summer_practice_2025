from fastapi import APIRouter, UploadFile, HTTPException
from app.file_handler import file_queue
import aiofiles
import uuid

router = APIRouter()

@router.post("/science/files/")
async def upload_file(file: UploadFile, author: str):
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