from __future__ import annotations

from typing import List, Type

from fastapi import APIRouter, Depends, File, Form, UploadFile

from auth import get_current_user
from crud import create_item, delete_item, get_item, list_items, update_item
from models import BaseItem


def build_router(model: Type[BaseItem], prefix: str) -> APIRouter:
    router = APIRouter(prefix=f"/{prefix}", tags=[prefix.capitalize()])

    # Crear registro con archivo opcional
    @router.post("", response_model=model, dependencies=[Depends(get_current_user)])
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

    # Actualizar registro (reemplaza archivo si se envia uno nuevo)
    @router.put("/{item_id}", response_model=model, dependencies=[Depends(get_current_user)])
    async def update(
        item_id: int,
        nombre: str = Form(...),
        descripcion: str = Form(""),
        file: UploadFile | None = File(None),
    ):
        return update_item(model, item_id, nombre, descripcion, file)

    # Eliminar registro y su archivo asociado
    @router.delete("/{item_id}", status_code=204, dependencies=[Depends(get_current_user)])
    def delete(item_id: int):
        delete_item(model, item_id)
        return None

    return router
