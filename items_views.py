from typing import Annotated
from fastapi import Path, APIRouter

# что-то не импортировать app из main.py
# и добаляем префикс, чтобы не отображать во вьюшках начальный пуцть (/items)
router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/")
def list_items():
    return ["Item1", "Item2", "Item3"]


@router.get("/latest/")
def get_item_latest():
    return {"item": {"id": "0", "name": "latest"}}


@router.get("/{item_id}/")
def get_item_by_id(item_id: Annotated[int, Path(ge=1, lt=1_000_000)]):
    return {"item": {"id": item_id}}
