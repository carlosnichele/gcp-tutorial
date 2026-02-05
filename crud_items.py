from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import Item as ItemModel
from schemas import ItemCreate, ItemRead

router = APIRouter()

@router.post("/items", response_model=ItemRead)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(ItemModel, item.id)
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")

    new_item = ItemModel(**item.dict())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


@router.get("/items", response_model=list[ItemRead])
async def list_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemModel))
    return result.scalars().all()


@router.get("/items/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await db.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item.name
    db_item.description = item.description

    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"message": "Item deleted"}
