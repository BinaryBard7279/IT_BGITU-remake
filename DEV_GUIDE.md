1. Как запустить проект у себя:

Клонируешь репо.
Создаешь файл .env.local 
Создаешь базу данных локально 
Запускаешь: pip install -r requirements.txt
Применяешь миграции: alembic upgrade head
Запускаешь сервер: python main.py

2. Как менять Базу Данных (ОЧЕНЬ ВАЖНО):
ЗАПРЕЩЕНО менять структуру БД руками или через create_all.
Если добавил таблицу/колонку в models.py:
В терминале: alembic revision --autogenerate -m "название_изменения"
Проверь созданный файл в папке alembic/versions.
Примени у себя: alembic upgrade head и проверь, что работает.
Только после этого делай Commit & Push.

3. Где смотреть данные:

Прод: https://admin.vinogradovnikita.ru (пароль спросишь)
