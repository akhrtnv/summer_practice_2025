import pytest
from app.file_handler import (
    MIN_DATE, MIN_VALUE, MIN_ROW_COUNT, MAX_ROW_COUNT,
    correct_start_time, correct_duration, correct_value, correct_row,
    parse_row, correct_file, calc_median
)
from datetime import datetime, timedelta

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
    assert correct_start_time(start_time) is expected

@pytest.mark.parametrize(
    "duration, expected",
    [
        (-1, False),
        (0, False),
        (1, True)
    ]
)
def test_correct_duration(duration, expected):
    assert correct_duration(duration) is expected

@pytest.mark.parametrize(
    "value, expected",
    [
        (MIN_VALUE - 1, False),
        (MIN_VALUE, True),
        (MIN_VALUE + 1, True)
    ]
)
def test_correct_value(value, expected):
    assert correct_value(value) is expected

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
    assert correct_row(start_time, duration, value) is expected

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
    assert parse_row(row) == expected

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
    assert correct_file(row_count, incorrect_count) is expected

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
    assert calc_median(values) == expected