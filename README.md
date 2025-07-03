## Запуск

1. Создание `venv`:

```
python -m venv venv
```

2. Активировация `venv`. На Windows:

```
venv\Scripts\activate
```

3. Установка зависимостей:

```
pip install -r requirements.txt
```

4. Запуск приложения из корня проекта:

```
uvicorn app.main:app
```

Swagger UI доступен по `http://127.0.0.1:8000/docs`.

5. Выполнение тестов:

```
python -m pytest
```