from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth import auth_router
from config import APP_TITLE, MEDIA_ROOT
from db import init_db
from models import Actividad, Programa, Recurso, Taller, Terapia
from routes import build_router

# App principal con CORS abierto para permitir consumo desde el frontend
app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded media from /media
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(auth_router)
app.include_router(build_router(Terapia, "terapias"))
app.include_router(build_router(Programa, "programas"))
app.include_router(build_router(Taller, "talleres"))
app.include_router(build_router(Actividad, "actividades"))
app.include_router(build_router(Recurso, "recursos"))
