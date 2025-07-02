from unittest.mock import MagicMock
from app.database.models import File, Value
from app.services.value_service import ValueService
from fastapi import HTTPException
from datetime import datetime

def test_get_values_file_not_found():
    mock_db = MagicMock()
    query = MagicMock()
    (query
     .filter.return_value
     .options.return_value
     .first.return_value 
    ) = None
    mock_db.query.return_value = query

    service = ValueService(db=mock_db)

    try:
        service.get_values_by_filename("missing.csv")
        assert False, "Ожидалось исключение HTTPException"
    except HTTPException as e:
        assert e.status_code == 404

def test_get_values_success():
    mock_db = MagicMock()
    
    mock_file = File(id=1,
                     filename="example.csv",
                     author="author",
                     created_at=datetime.now())
    
    mock_file.values = [Value(id=1,
                              file_id=1,
                              start_time=datetime(year=2025, month=1, day=1),
                              duration=60,
                              value=5.5)]
    
    query = MagicMock()
    (query
     .filter.return_value
     .options.return_value
     .first.return_value 
    ) = mock_file
    mock_db.query.return_value = query

    service = ValueService(db=mock_db)

    result = service.get_values_by_filename("example.csv")

    assert result["file"].filename == "example.csv"
    assert result["values"][0].value == 5.5