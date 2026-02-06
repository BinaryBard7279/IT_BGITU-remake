FROM python:3.11-slim

WORKDIR /code 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ... (начало файла без изменений)
COPY . .

# --- ИСПРАВЛЕНИЕ НАЧАЛО ---
# Явно создаем папку для загрузок
RUN mkdir -p /code/app/uploads

# Раздаем права пользователю appuser на всю папку проекта
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /code
# --- ИСПРАВЛЕНИЕ КОНЕЦ ---

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
