from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, LoginRequest
from app.security import verify_password, get_password_hash
from app.jwt_manager import jwt_manager

router = APIRouter(prefix="/admin", tags=["Authentification"])

# Authentification
@router.get("/")
async def admin_root():
    return {
        "Эндпоинты": {
            "POST /admin/": "Аутентификация пользователя",
            "POST /admin/hash-password": "Получить хэш пароля для ручного создания пользователя (Временое решение)"
        }
    }

@router.post("/", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    access_token = jwt_manager.create_access_token(token_data)
    
    return Token(access_token=access_token)

# Password to hash
@router.post("/hash-password")
async def hash_password_endpoint(password: str = Form(..., min_length=6)):
    """
    Получить хэш пароля для ручного создания пользователя в БД.
    
    Внимание: Bcrypt ограничивает пароли 72 байтами.
    Если ваш пароль содержит не-ASCII символы или очень длинный,
    он будет автоматически обрезан.
    """
    password_bytes = password.encode('utf-8')
    original_length = len(password_bytes)
    
    if original_length > 72:
        warning = f"Внимание: Пароль длиннее 72 байт ({original_length} байт). Он будет обрезан для совместимости с bcrypt."
    else:
        warning = None
    
    hashed_password = get_password_hash(password)
    
    return {
        "original_password": password,
        "password_length_bytes": original_length,
        "warning": warning,
        "hashed_password": hashed_password,
        "Пример запроса sql": f"""
-- SQL запрос для создания пользователя в PostgreSQL:
INSERT INTO users (name, email, hashed_password) 
VALUES ('Администратор', 'admin@university.ru', '{hashed_password}');
        """
    }