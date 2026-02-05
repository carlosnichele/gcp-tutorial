from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM

from database import get_db
from models import Item as ItemModel
from schemas import ItemCreate, ItemRead

import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


logger = logging.getLogger("items")

router = APIRouter()

@router.post("/items", response_model=ItemRead)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating item with id={item.id}")
    existing = await db.get(ItemModel, item.id)
    if existing:
        logger.warning(f"Item {item.id} already exists")
        raise HTTPException(status_code=400, detail="Item already exists")

    new_item = ItemModel(**item.dict())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    logger.info(f"Item {item.id} created successfully")
    return new_item


@router.get("/items", response_model=list[ItemRead])
async def list_items( skip: int = 0,
                      limit: int = 10,
                      db: AsyncSession = Depends(get_db),
                      user: str = Depends(get_current_user) ):
    result = await db.execute( select(ItemModel).offset(skip).limit(limit) )
    return result.scalars().all()



@router.get("/items/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Fetching item {item_id}")
    item = await db.get(ItemModel, item_id)
    if not item:
        logger.error(f"Item {item_id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, item: ItemCreate, db: AsyncSession = Depends(get_db)):
    if item_id != item.id:
        raise HTTPException(status_code=400, detail="ID mismatch")

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
