from unittest.mock import MagicMock
from app.database.models import File, Result
from app.services.result_service import ResultService
from datetime import datetime
from fastapi import HTTPException

def test_get_results_by_filename_success():        
    file = File(id=1,
                filename="example.csv",
                author="author",
                created_at=datetime(year=2025, month=1, day=10))

    file.result = Result(id=1,
                         file_id = 1,
                         first_start = datetime(year=2025, month=1, day=1),
                         last_start = datetime(year=2025, month=1, day=9),
                         min_duration = 60,
                         max_duration = 120,
                         avg_duration = 90,
                         avg_value = 3.0,
                         median_value = 2.5,
                         min_value = 1.0,
                         max_value = 5.0,
                         experiment_count = 2)

    mock_db = MagicMock()
    query = MagicMock()
    (query
     .filter.return_value
     .options.return_value
     .first.return_value
    ) = file
    mock_db.query.return_value = query

    service = ResultService(db=mock_db)

    response = service.get_results_by_filename("example.csv")

    assert query.filter.call_count == 1
    assert response[0]["file"].filename == "example.csv"
    assert response[0]["result"].file_id == 1

def test_get_results_file_not_found():
    mock_db = MagicMock()
    query = MagicMock()
    (query
     .filter.return_value
     .options.return_value
     .first.return_value 
    ) = None
    mock_db.query.return_value = query

    service = ResultService(db=mock_db)

    try:
        service.get_results_by_filename("missing.csv")
        assert False, "Ожидалось исключение HTTPException"
    except HTTPException as e:
        assert e.status_code == 404

def test_get_results_by_min_avg_value_success():
    result = Result(id=1,
                    file_id = 1,
                    first_start = datetime(year=2025, month=1, day=1),
                    last_start = datetime(year=2025, month=1, day=9),
                    min_duration = 60,
                    max_duration = 120,
                    avg_duration = 90,
                    avg_value = 3.0,
                    median_value = 2.5,
                    min_value = 1.0,
                    max_value = 5.0,
                    experiment_count = 2)
    
    result.file = File(id=1,
                       filename="example.csv",
                       author="author",
                       created_at=datetime(year=2025, month=1, day=10))

    min_avg_value = 2.0

    mock_db = MagicMock()
    query = MagicMock()

    mock_db.query.return_value = query
    query.filter.return_value = query
    query.options.return_value.all.return_value = [result]

    service = ResultService(db=mock_db)

    response = service.get_filtered_results(
        min_avg_value=min_avg_value,
        max_avg_value=None,
        min_avg_duration=None,
        max_avg_duration=None
    )

    # проверяем, что сработал нужный фильтр
    assert query.filter.call_count == 1
    called_with = query.filter.call_args[0][0]
    assert called_with.left == Result.avg_value
    assert called_with.right.value == min_avg_value

    assert response[0]["file"].filename == "example.csv"