from ..database.models import File, Value, Result
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from os import remove
import asyncio
import csv

class FileHandler:
    MIN_DATE = datetime(2000, 1, 1)
    MIN_VALUE = 0
    MIN_ROW_COUNT = 1
    MAX_ROW_COUNT = 10000
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    # обработкчик файлов: проверяет корректность, добавляет записи в таблицы
    async def run_handler(self, file_queue: asyncio.Queue):
        while True:
            filename, filepath, author = await file_queue.get()

            try:
                await self.process_file(filename, filepath, author)
            except Exception as e:
                print(f"[handler] ошибка при добавлении записи: {e}")
            finally:
                remove(filepath)  # удаляем временный файл после обработки
                file_queue.task_done()

    async def process_file(self, filename: str, filepath: str, author: str):
        row_count, incorrect_rows = self.validate_rows(filepath)
        
        # отбрасываем некорректный файл
        if not self.correct_file(row_count, len(incorrect_rows)):
            return
        
        db = self.db_session_factory()
        try:
            # добавляем запись в таблицу файлов
            file_id = self.add_file_info(filename, author, db)
            
            # добавлние корректных строк в таблицу значений
            self.add_values(filepath, file_id, incorrect_rows, db)
            
            # вычисление показателей и запись в таблицу результатов
            self.add_result(file_id, db)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def validate_rows(self, filepath: str):
        row_count = 0
        incorrect_rows = []

        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            next(reader)  # пропускаем строку с заголовоками

            for i, row in enumerate(reader, start=1):  # перебираем строки с их индексами
                row_count += 1
                start_time, duration, value = self.parse_row(row)
                if not self.correct_row(start_time, duration, value):
                    incorrect_rows.append(i)

        return row_count, incorrect_rows

    def add_file_info(self, filename: str, author: str, db: Session):
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

        return record.id # id только что добавленной записи

    def add_values(self,
                   filepath       : str, 
                   file_id        : int, 
                   incorrect_rows : list[int], 
                   db             : Session
    ):
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            next(reader)

            for i, row in enumerate(reader):
                if i in incorrect_rows:
                    continue

                start_time, duration, value = self.parse_row(row)

                record = Value(
                    file_id=file_id,
                    start_time=start_time,
                    duration=duration,
                    value=value
                )
                db.add(record)
                db.flush()

    def add_result(self, file_id: int, db: Session):
        # запрос с получением общих метрик экспериментов файла
        query = db.query(
            func.min(Value.start_time),
            func.max(Value.start_time),
            func.min(Value.duration),
            func.max(Value.duration),
            func.round(func.avg(Value.duration)),
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
        median_value = FileHandler.calc_median([v[0] for v in values])
    
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

    def correct_start_time(self, start_time: datetime):
        return self.MIN_DATE <= start_time < datetime.now()

    def correct_duration(self, duration: int):
        return 0 < duration

    def correct_value(self, value: float):
        return self.MIN_VALUE <= value

    def correct_row(self, start_time: datetime, duration: int, value: float):
        if not self.correct_start_time(start_time):
            return False
        if not self.correct_duration(duration):
            return False
        if not self.correct_value(value):
            return False 
        return True

    def parse_row(self, row: list):
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

    def correct_file(self, row_count: int, incorrect_count: int):
        if not (self.MIN_ROW_COUNT <= row_count <= self.MAX_ROW_COUNT):
            return False
        if not (incorrect_count < row_count):
            return False
        return True

    @staticmethod
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