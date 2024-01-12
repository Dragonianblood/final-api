from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Items
from database import get_db
from .auth import get_current_user

router = APIRouter()


class Item(BaseModel):
    id: Optional[int] = None
    address: str = Field(min_length=5)
    order: str = Field(min_length=3, max_length=250)
    amount_paid: int = Field(gt=0, lt=100)
    nice_rating: bool = Field(default=0)
    ordered_on: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "address": "nowhere",
                "order": "coffee",
                "amount_paid": 5,
                "nice_rating": 1
            }
        }


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_tasks(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Items).filter(Items.name == current_user.get("id")).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(item: Item, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_item = Items(**item.model_dump(), name=current_user.get("id"))
    db.add(new_item)
    db.commit()


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(task_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    task = db.query(Items).filter(Items.id == task_id).filter(Items.name == current_user.get("id")).first()
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail=f"Task not found with id#{task_id}")


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task_by_id(item_data: Item, task_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    item = db.query(Items).filter(Items.id == task_id).filter(Items.name == current_user.get("id"))
    if item is None:
        raise HTTPException(status_code=404, detail=f"Task not found with id#{task_id}")
    item.name = item_data.name
    item.address = item_data.address
    item.order = item_data.order
    item.amount_paid = item_data.amount_paid
    item.nice_rating = item_data.nice_rating

    db.add(item)
    db.commit()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(task_id: int = Path(gt=0), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    delete_item = db.query(Items).filter(Items.id == task_id).filter(Items.name == current_user.get("id"))

    if delete_item is None:
        return {"msg": f"Task with id#{task_id} was not found"}

    db.query(Items).filter(Items.id == task_id).delete()

    db.commit()
