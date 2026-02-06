import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, cms, public
from fastapi.templating import Jinja2Templates

app = FastAPI(title="IT BGITU Remake")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(cms.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)