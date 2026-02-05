from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()
db: Dict[int, dict] = {}

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

@router.post("/items")
def create_item(item: Item):
    if item.id in db:
        raise HTTPException(status_code=400, detail="Item already exists")
    db[item.id] = item.dict()
    return db[item.id]

@router.get("/items")
def list_items():
    return list(db.values())

@router.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

@router.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    db[item_id] = item.dict()
    return db[item_id]

@router.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db.pop(item_id)
