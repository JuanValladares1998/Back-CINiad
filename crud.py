from __future__ import annotations

from typing import Type

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from db import engine
from media_utils import remove_media_files, save_file
from models import BaseItem


def create_item(model: Type[BaseItem], nombre: str, descripcion: str, file: UploadFile | None):
    media_url = media_card_url = media_tipo = media_nombre = None
    if file:
        media_url, media_card_url, media_tipo, media_nombre = save_file(file)
    obj = model(
        nombre=nombre,
        descripcion=descripcion or None,
        media_url=media_url,
        media_card_url=media_card_url,
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


def update_item(model: Type[BaseItem], item_id: int, nombre: str, descripcion: str, file: UploadFile | None):
    with Session(engine) as session:
        obj = session.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        if file:
            remove_media_files(obj.media_url, obj.media_card_url)
            media_url, media_card_url, media_tipo, media_nombre = save_file(file)
            obj.media_url = media_url
            obj.media_card_url = media_card_url
            obj.media_tipo = media_tipo
            obj.media_nombre = media_nombre
        obj.nombre = nombre
        obj.descripcion = descripcion or None
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj


def delete_item(model: Type[BaseItem], item_id: int):
    with Session(engine) as session:
        obj = session.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        remove_media_files(obj.media_url, obj.media_card_url)
        session.delete(obj)
        session.commit()
