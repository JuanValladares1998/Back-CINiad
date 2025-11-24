from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Type

from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Rutas base para medios y base de datos
BASE_DIR = Path(__file__).resolve().parent
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Conexion simple con SQLite; cambialo por Postgres en produccion
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=False)


# Modelo base con campos comunes a todas las tablas
class BaseItem(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    media_url: Optional[str] = None
    media_tipo: Optional[str] = None  # "image" or "video"
    media_nombre: Optional[str] = None


class Terapia(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Programa(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Taller(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Actividad(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Recurso(BaseItem, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# App principal con CORS abierto para permitir consumo desde el frontend
app = FastAPI(title="Back-CINiad")

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
    SQLModel.metadata.create_all(engine)


# Helpers para manejo de archivos y operaciones CRUD basicas
def detect_media_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    if ext in image_exts:
        return "image"
    if ext in video_exts:
        return "video"
    raise HTTPException(status_code=400, detail="Formato de archivo no permitido")


def save_file(file: UploadFile) -> tuple[str, str, str]:
    media_tipo = detect_media_type(file.filename)
    filename = f"{uuid.uuid4().hex}{Path(file.filename).suffix.lower()}"
    destination = MEDIA_ROOT / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    media_url = f"/media/{filename}"
    return media_url, media_tipo, file.filename


def create_item(model: Type[BaseItem], nombre: str, descripcion: str, file: UploadFile | None):
    media_url = media_tipo = media_nombre = None
    if file:
        media_url, media_tipo, media_nombre = save_file(file)
    obj = model(
        nombre=nombre,
        descripcion=descripcion or None,
        media_url=media_url,
        media_tipo=media_tipo,
        media_nombre=media_nombre,
    )
    with Session(engine) as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj


def list_items(model: Type[BaseItem]):
    with Session(engine) as session:
        return session.exec(select(model)).all()


def get_item(model: Type[BaseItem], item_id: int):
    with Session(engine) as session:
        result = session.get(model, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return result


def build_router(model: Type[BaseItem], prefix: str) -> APIRouter:
    router = APIRouter(prefix=f"/{prefix}", tags=[prefix.capitalize()])

    # Crear registro con archivo opcional
    @router.post("", response_model=model)
    async def create(
        nombre: str = Form(...),
        descripcion: str = Form(""),
        file: UploadFile | None = File(None),
    ):
        return create_item(model, nombre, descripcion, file)

    # Listar todos los registros
    @router.get("", response_model=List[model])
    def list_all():
        return list_items(model)

    # Obtener detalle por id
    @router.get("/{item_id}", response_model=model)
    def retrieve(item_id: int):
        return get_item(model, item_id)

    return router


app.include_router(build_router(Terapia, "terapias"))
app.include_router(build_router(Programa, "programas"))
app.include_router(build_router(Taller, "talleres"))
app.include_router(build_router(Actividad, "actividades"))
app.include_router(build_router(Recurso, "recursos"))
