from fastapi import (
    APIRouter, UploadFile, Form, Query, Depends
)
from fastapi import File as FileForm
from typing import List, Optional
from .schemas import ResultResponse, ValuesResponse
from .services.file_service import FileService
from .services.result_service import ResultService
from .services.value_service import ValueService

router = APIRouter()

@router.post("/science/files/")
async def post_file(
    file         : UploadFile = FileForm(...), 
    author       : str = Form(...),
    file_service : FileService = Depends(FileService.get_service)
):
    await file_service.add_file(file, author)
    return {"message": "Файл принят для обработки"}
    
    
@router.get("/science/results/", response_model=List[ResultResponse])
def get_results(
    filename         : Optional[str] = Query(None, alias="fileName"),
    min_avg_value    : Optional[float] = Query(None, alias="minAvgValue"),
    max_avg_value    : Optional[float] = Query(None, alias="maxAvgValue"),
    min_avg_duration : Optional[int] = Query(None, alias="minAvgDuration"),
    max_avg_duration : Optional[int] = Query(None, alias="maxAvgDuration"),
    result_service: ResultService = Depends(ResultService.get_service)
):
    if filename:
        return result_service.get_results_by_filename(filename)
    
    return result_service.get_filtered_results(
        min_avg_value=min_avg_value,
        max_avg_value=max_avg_value,
        min_avg_duration=min_avg_duration,
        max_avg_duration=max_avg_duration
    )

@router.get("/science/values/{fileName}", response_model=ValuesResponse)
def get_values(
    fileName: str,
    service: ValueService = Depends(ValueService.get_service)
):
    return service.get_values_by_filename(fileName)