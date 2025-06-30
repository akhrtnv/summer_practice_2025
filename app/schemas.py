from pydantic import BaseModel
from datetime import datetime
from typing import List

class File(BaseModel):
    filename   : str
    author     : str
    created_at : datetime

    class Config:
        from_attributes = True

class Result(BaseModel):
    first_start      : datetime
    last_start       : datetime
    min_duration     : int
    max_duration     : int
    avg_duration     : int
    avg_value        : float
    median_value     : float
    min_value        : float
    max_value        : float
    experiment_count : int

    class Config:
        from_attributes = True

class ResultResponse(BaseModel):
    file   : File
    result : Result

class Value(BaseModel):
    start_time : datetime
    duration   : int
    value      : float

class ValuesResponse(BaseModel):
    file   : File
    values : List[Value]