from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class FileDTO(BaseModel):
    filename   : str
    author     : str
    created_at : datetime

    model_config = ConfigDict(from_attributes = True)

class ResultDTO(BaseModel):
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

    model_config = ConfigDict(from_attributes = True)
    
class ResultResponse(BaseModel):
    file   : FileDTO
    result : ResultDTO

class Value(BaseModel):
    start_time : datetime
    duration   : int
    value      : float

class ValuesResponse(BaseModel):
    file   : FileDTO
    values : List[Value]