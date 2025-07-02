from fastapi import UploadFile, HTTPException, Depends
from uuid import uuid4
from .file_queue import get_queue
import asyncio
import aiofiles

class FileService:
    def __init__(self, file_queue: asyncio.Queue):
        self.file_queue = file_queue  # очередь файлов для обработки
    
    async def add_file(self, file: UploadFile, author: str):
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(400, detail="Ожидался файл с расширением .csv")
        
        filepath = f"./tmp/{uuid4()}.csv"
    
        async with aiofiles.open(filepath, "wb") as out_file:  # открываем файл для записи
            while chunk := await file.read(1024):              # считываем из полученного файла фрагмент
                await out_file.write(chunk)                    # записываем

        await self.file_queue.put((file.filename, filepath, author))  # добавляем в очередь обработки
        await file.close()
    
    def get_service(file_queue: asyncio.Queue = Depends(get_queue)):
        return FileService(file_queue)