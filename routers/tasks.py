from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Tasks
from database import get_db

router = APIRouter()


class Task(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=3)
    address: str = Field(min_length=5)
    order: str = Field(min_length=3, max_length=250)
    amount_paid: int = Field(gt=0, lt=100)
    nice_rating: bool = Field(default=0)
    created_on: datetime = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "jeff",
                "address": "nowhere",
                "order": "coffee",
                "amount_paid": 5,
                "nice_rating": 1
            }
        }








@router.get("", status_code=status.HTTP_200_OK)
async def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Tasks).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(task: Task, db: Session = Depends(get_db)):
    new_task = Tasks(**task.model_dump())
    db.add(new_task)
    db.commit()


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(task_id: int = Path(gt=0), db: Session = Depends(get_db)):
    task = db.query(Tasks).filter(task_id == Tasks.id).first()
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail=f"Task not found with id#{task_id}")


@router.put("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task_by_id(task_id: int = Path(gt=0), task_data=Task, db: Session = Depends(get_db)):
    task = db.query(Tasks).filter(task_id == Tasks.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found with id#{task_id}")
    task.name = task_data.name
    task.address = task_data.address
    task.order = task_data.order
    task.amount_paid = task_data.amount_paid
    task.nice_rating = task_data.nice_rating

    db.add(task)
    db.commit()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(task_id: int = Path(gt=0), db: Session = Depends(get_db)):
    delete_task = db.query().filter(Tasks.id == task_id).first()

    if delete_task is None:
        return {"msg": f"Task with id#{task_id} was not found"}

    db.query().filter(Tasks.id == task_id).delete()

    db.commit()
