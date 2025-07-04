from app.services.file_handler import FileHandler
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from app.database.models import Value
import pytest
import csv

MIN_DATE = FileHandler.MIN_DATE
MIN_VALUE = FileHandler.MIN_VALUE
MIN_ROW_COUNT = FileHandler.MIN_ROW_COUNT
MAX_ROW_COUNT = FileHandler.MAX_ROW_COUNT

fh = FileHandler(db_session_factory=None, file_queue=None)

@pytest.mark.parametrize(
    "start_time, expected",
    [
        (MIN_DATE - timedelta(days=1), False),
        (MIN_DATE, True),
        (MIN_DATE + timedelta(days=1), True),
        (datetime.now(), True),
        (datetime.now() + timedelta(days=1), False)
    ]
)
def test_correct_start_time(start_time, expected):
    assert fh.correct_start_time(start_time) is expected

@pytest.mark.parametrize(
    "duration, expected",
    [
        (-1, False),
        (0, False),
        (1, True)
    ]
)
def test_correct_duration(duration, expected):
    assert fh.correct_duration(duration) is expected

@pytest.mark.parametrize(
    "value, expected",
    [
        (MIN_VALUE - 1, False),
        (MIN_VALUE, True),
        (MIN_VALUE + 1, True)
    ]
)
def test_correct_value(value, expected):
    assert fh.correct_value(value) is expected

@pytest.mark.parametrize(
    "start_time, duration, value, expected",
    [
        (MIN_DATE, 1, MIN_VALUE, True),
        (MIN_DATE - timedelta(days=1), 1, MIN_VALUE + 1, False),
        (MIN_DATE + timedelta(days=1), 0, MIN_VALUE + 1, False),
        (datetime.now(), 1, MIN_VALUE - 1, False),
        (datetime.now() + timedelta(days=1), 1, MIN_VALUE + 1, False)
    ]
)
def test_correct_row(start_time, duration, value, expected):
    assert fh.correct_row(start_time, duration, value) is expected

@pytest.mark.parametrize(
    "row, expected",
    [
        (["2025-06-01_10-00-00", "60", "42.5"], (datetime(2025, 6, 1, 10), 60, 42.5)),
        (["too", "short"], None),
        (["2025.06.01-10.00.00", "60", "42.5"], None),
        (["2025-06-01_10-00-00", "str", "42.5"], None),
        (["2025-06-01_10-00-00", "60", "str"], None)
    ]
)
def test_parse_row(row, expected):
    assert fh.parse_row(row) == expected

@pytest.mark.parametrize(
    "row_count, incorrect_count, expected",
    [
        (MIN_ROW_COUNT - 1, 0, False),
        (MIN_ROW_COUNT, 0, True),
        (MIN_ROW_COUNT + 1, 0, True),
        (MIN_ROW_COUNT, MIN_ROW_COUNT, False),
        (MAX_ROW_COUNT, MAX_ROW_COUNT - 1, True),
        (MAX_ROW_COUNT + 1, 0, False),
        (MIN_ROW_COUNT, MIN_ROW_COUNT + 1, False)
    ]
)
def test_correct_file(row_count, incorrect_count, expected):
    assert fh.correct_file(row_count, incorrect_count) is expected

@pytest.mark.parametrize(
    "values, expected",
    [
        ([1, 2, 3, 4, 1000], 3),
        ([4000, 2000, 3000, 1000], 2500),
        ([1], 1),
        ([-1, -2, -3, -4], -2.5),
        ([], None)
    ]
)
def test_calc_median(values, expected):
    assert fh.calc_median(values) == expected

@pytest.mark.asyncio
async def test_validate_rows(tmp_path):
    # создаём путь к временной заглушке
    dummy_csv = tmp_path / "test.csv"

    # наполняем CSV-файл тестовыми строками
    with open(dummy_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["start_time", "duration", "value"])
        writer.writerow(["2025-01-01_12-00-00", "60", "1.5"])      # корректная строка
        writer.writerow(["1990-01-01 $$$ 12-00-00", "60", "1.0"])  # некорректная дата
        writer.writerow(["2025-01-01_12-00-00", "-10", "1.0"])     # некорректная длительность

    # вызываем функцию
    total_rows, incorrect_rows = fh.validate_rows(str(dummy_csv))

    assert total_rows == 3
    assert incorrect_rows == [2, 3]

def test_add_values(tmp_path):
    # подготовим временный CSV-файл, данные из прошлого теста
    file_path = tmp_path / "values.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["start_time", "duration", "value"])
        writer.writerow(["2025-01-01_12-00-00", "60", "1.5"])      # корректная строка
        writer.writerow(["1990-01-01 $$$ 12-00-00", "60", "1.0"])  # некорректная дата
        writer.writerow(["2025-01-01_12-00-00", "-10", "1.0"])     # некорректная длительность

    mock_db = MagicMock()

    fh.add_values(str(file_path), file_id=42, incorrect_rows=[2, 3], db=mock_db)

    mock_db.add.assert_called_once()
    args, _ = mock_db.add.call_args
    added_value: Value = args[0]
    assert added_value.file_id == 42
    assert added_value.duration == 60
    assert added_value.value == 1.5

    assert mock_db.flush.call_count == 1