from app.database import session
from app.models import File, Value, Result
from datetime import datetime
import asyncio
import csv

file_queue = asyncio.Queue()

MIN_DATE = datetime(2000, 1, 1)
MIN_VALUE = 0
MIN_ROW_COUNT = 1
MAX_ROW_COUNT = 10000

def correct_start_time(start_time: datetime):
    return MIN_DATE <= start_time < datetime.now()

def correct_duration(duration: int):
    return duration > 0

def correct_value(value: float):
    return MIN_VALUE <= value

def correct_row(start_time: datetime, duration: int, value: float):
    if not correct_start_time(start_time):
        return False
    if not correct_duration(duration):
        return False
    if not correct_value(value):
        return False 
    return True

def parse_row(row: list):
    start_time_str, duration_str, value_str = row
                
    start_time = datetime.strptime(start_time_str, "%Y-%m-%d_%H-%M-%S")
    duration = int(duration_str)
    value = float(value_str)

    return start_time, duration, value

async def handler():
    while True:
        filename, filepath, author = await file_queue.get()
        
        # считаем общее число строк и некорректные строки
        row_count = 0
        incorrect_rows = []
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            next(reader)  # пропускаем заголовок

            for i, row in enumerate(reader):
                row_count += 1

                start_time, duration, value = parse_row(row)

                if not correct_row(start_time, duration, value):
                    incorrect_rows.append(i)
        
        if not (MIN_ROW_COUNT <= row_count <= MAX_ROW_COUNT) or len(incorrect_rows) == row_count:
            continue

        db = session()
        try:
            # из таблицы files удаляем файл с таким же названием, если есть
            existing = db.query(File).filter(File.filename == filename).first()
            if existing:
                db.delete(existing)
                db.flush()  # сброс для выполнения удаления
            
            # добавляем новую запись в таблицу files 
            record = File(
                filename=filename,
                author=author,
                created_at=datetime.now()
            )
            db.add(record)
            db.flush()

            with open(filepath, "r", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # пропускаем заголовок

                for i, row in enumerate(reader):
                    if i in incorrect_rows:
                        continue
                    
                    start_time, duration, value = parse_row(row)
                    
                    record = Value(
                        start_time=start_time,
                        duration=duration,
                        value=value
                    )
                    db.add(record)
            db.flush()

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[handler] ошибка при добавлении записи: {e}")
        finally:
            db.close()
            file_queue.task_done()