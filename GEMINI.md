# IT BGITU Remake - Project Context

## Project Overview

This is a Python-based backend application built using the **FastAPI** framework. It appears to be a remake of an IT-related service (IT BGITU), providing web endpoints, static files serving, and an administrative interface.

**Key Technologies:**
*   **Web Framework:** FastAPI
*   **ASGI Server:** Uvicorn
*   **Database ORM:** SQLAlchemy (with `asyncpg` for PostgreSQL async support)
*   **Database Migrations:** Alembic
*   **Data Validation:** Pydantic
*   **Templating:** Jinja2
*   **Admin Panel:** sqladmin
*   **Security/Auth:** passlib, python-jose

## Architecture and Structure

The project follows a standard FastAPI project structure:

*   `app/`: The main application package.
    *   `app/main.py`: The entry point of the application, configuring FastAPI, middleware (including custom performance monitoring), static files, and routing.
    *   `app/models/`: SQLAlchemy database models (e.g., `user.py`, `subject.py`, `teacher.py`).
    *   `app/schemas/`: Pydantic models for request/response validation.
    *   `app/routers/`: FastAPI route handlers (`public`, `auth`, `cms`).
    *   `app/core/`, `app/dependencies.py`, `app/security.py`: Core logic, auth, and dependency injection.
    *   `app/admin.py`: Configuration for the `sqladmin` interface.
    *   `app/static/` & `app/templates/`: Static assets and Jinja2 templates for frontend rendering.
*   `alembic/`: Contains database migration scripts.
*   `tests/`: Contains test suite using `pytest`.
*   `pyproject.toml`: Configuration for development tools like `ruff` and `pytest`.
*   `requirements.txt`: Project dependencies.

## Building and Running

**Prerequisites:**
*   Python 3.12 (as specified in `pyproject.toml`)
*   A running PostgreSQL database.

**Setup:**
1.  Create and activate a virtual environment: `python -m venv venv` and `source venv/bin/activate` (or `venv\Scripts\activate` on Windows).
2.  Install dependencies: `pip install -r requirements.txt`.

**Running the Application:**
You can run the application directly using the `main.py` script, which uses `uvicorn`:
```bash
python app/main.py
```
Or by running Uvicorn directly:
```bash
uvicorn app.main:app --reload
```

**Database Migrations:**
To apply database changes:
```bash
alembic upgrade head
```

## Development Conventions

*   **Linting and Formatting:** The project uses **Ruff** for fast linting and formatting. Configuration in `pyproject.toml` specifies a `line-length` of 100, target version Python 3.12, and specific rules (select = `["E", "F", "W", "I"]`).
*   **Testing:** **Pytest** with `pytest-asyncio` is used for testing. Tests are located in the `tests/` directory. Run tests using:
    ```bash
    pytest
    ```
*   **Asynchronous Code:** The application makes heavy use of asynchronous Python (`async`/`await`), utilizing `asyncpg` for non-blocking database operations.
*   **Performance Monitoring:** The application includes a custom `PerformanceMiddleware` in `main.py` that logs execution times for endpoints (excluding static files).
