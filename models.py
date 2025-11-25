from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class BaseItem(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    media_url: Optional[str] = None
    media_card_url: Optional[str] = None
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
