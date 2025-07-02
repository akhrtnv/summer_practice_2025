from unittest.mock import AsyncMock, patch, ANY
import pytest
from fastapi import UploadFile, HTTPException
from app.services.file_service import FileService

@pytest.mark.asyncio
async def test_post_file_valid_csv():
    file = AsyncMock(spec=UploadFile)
    file.filename = "test.csv"
    file.read = AsyncMock(return_value=b"")  # пустой файл
    file.close = AsyncMock()

    # мокаем file_queue
    file_queue = AsyncMock()

    service = FileService(file_queue)

    # мокаем aiofiles.open
    with patch("aiofiles.open") as mock_open:
        # настраиваем мок для поддержки async with
        mock_file = AsyncMock()
        mock_file.write = AsyncMock()
        mock_open.return_value.__aenter__.return_value = mock_file
        mock_open.return_value.__aexit__ = AsyncMock()

        response = await service.add_file(file, "author")

        # проверяем, что aiofiles.open вызван
        mock_open.assert_called_once()

        # проверяем, что данные добавлены в очередь
        file_queue.put.assert_awaited_once_with(("test.csv", ANY, "author"))

        # проверяем ответ
        assert response == {"message": "Файл принят для обработки"}

@pytest.mark.asyncio
async def test_post_file_invalid_extension():
    file = AsyncMock(spec=UploadFile)
    file.filename = "test.txt"

    file_queue = AsyncMock()

    service = FileService(file_queue)

    with pytest.raises(HTTPException) as e:
        await service.add_file(file=file, author="test_author")

    assert e.value.status_code == 400
    assert e.value.detail == "Ожидался файл с расширением .csv"