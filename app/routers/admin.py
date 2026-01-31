from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/")
async def admin_home():
    return {"message": "Здесь будет админка CMS"}
