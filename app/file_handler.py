from .database.database import session
from .database.models import File, Value, Result
from datetime import datetime
from sqlalchemy import func
from os import remove
import asyncio
import csv

file_queue = asyncio.Queue()

MIN_DATE = datetime(2000, 1, 1)
MIN_VALUE = 0
MIN_ROW_COUNT = 1
MAX_ROW_COUNT = 10000

# обработкчик файлов: проверяет корректность, добавляет записи в таблицы
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
        
        # отбрасываем некорректный файл
        if not correct_file(row_count, len(incorrect_rows)):
            continue

        db = session()
        try:
            # из таблицы files удаляем файл с таким же названием, если есть
            existing = db.query(File).filter(File.filename == filename).first()
            if existing:
                db.delete(existing)
                db.flush()  # сброс изменений в БД
            
            # добавляем новую запись в таблицу files 
            record = File(
                filename=filename,
                author=author,
                created_at=datetime.now()
            )
            db.add(record)
            db.flush()

            file_id = record.id # id только что добавленной записи

            # запись корректных строк в таблицу values
            with open(filepath, "r", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)  # пропускаем заголовок

                for i, row in enumerate(reader):
                    if i in incorrect_rows:
                        continue
                    
                    start_time, duration, value = parse_row(row)
                    
                    record = Value(
                        file_id=file_id,
                        start_time=start_time,
                        duration=duration,
                        value=value
                    )
                    db.add(record)
            db.flush()

            # TODO: проверь корректность типов полей в бд

            # запрос с получением общих метрик экспериментов файла
            query = db.query(
                func.min(Value.start_time),
                func.max(Value.start_time),
                func.min(Value.duration),
                func.max(Value.duration),
                func.avg(Value.duration),
                func.avg(Value.value),
                func.min(Value.value),
                func.max(Value.value),
                func.count(Value.id)
            ).filter(Value.file_id == file_id)

            # распаковка запроса
            (first_start,
             last_start,
             min_duration,
             max_duration,
             avg_duration,
             avg_value,
             min_value,
             max_value,
             experiment_count
            ) = query.one()

            # получение медианы
            values = (
                db.query(Value.value)
                .filter(Value.file_id == file_id)
                .all()
            )
            median_value = calc_median([v[0] for v in values])

            record = Result(
                file_id = file_id,
                first_start = first_start,
                last_start = last_start,
                min_duration = min_duration,
                max_duration = max_duration,
                avg_duration = avg_duration,
                avg_value = avg_value,
                median_value = median_value,
                min_value = min_value,
                max_value = max_value,
                experiment_count = experiment_count
            )
            db.add(record)
            db.commit()  # фиксируем все изменения
        except Exception as e:
            db.rollback()
            print(f"[handler] ошибка при добавлении записи: {e}")
        finally:
            db.close()
            remove(filepath)  # удаляем временный файл после обработки
            file_queue.task_done()
            
def correct_start_time(start_time: datetime):
    return MIN_DATE <= start_time < datetime.now()

def correct_duration(duration: int):
    return 0 < duration

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
    if len(row) != 3:
        return None

    start_time_str, duration_str, value_str = row
    
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d_%H-%M-%S")
        duration = int(duration_str)
        value = float(value_str)
        return start_time, duration, value
    except (ValueError, TypeError):
        return None
    
def correct_file(row_count: int, incorrect_count: int):
    if not (MIN_ROW_COUNT <= row_count <= MAX_ROW_COUNT):
        return False
    if not (incorrect_count < row_count):
        return False
    return True

def calc_median(values: list[float]):
    n = len(values)
    
    if n == 0:
        return None
    
    sorted_values = sorted(values)

    middle = n // 2

    if n % 2 == 1:
        return sorted_values[middle]
    else:
        return (sorted_values[middle - 1] + sorted_values[middle]) / 2  