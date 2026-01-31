FROM python:3.11-slim

WORKDIR /code 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаем юзера для безопасности
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /code
USER appuser

# ЗАПУСК: 
# Используем модуль app.main, так как файл теперь лежит в папке app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
