import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv(".env.local")
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class JWTManager:
    def __init__(self):
        if not SECRET_KEY or SECRET_KEY == "fallback-secret-key-change-me":
            raise ValueError("SECRET_KEY не установлен в .env.local!")
        
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[int]:
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id:
            try:
                return int(user_id)
            except (ValueError, TypeError):
                return None
        return None

jwt_manager = JWTManager()