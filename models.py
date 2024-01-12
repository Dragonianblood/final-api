from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.utcnow)

class Items(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, ForeignKey("users.id"))
    address = Column(String)
    order = Column(String)
    amount_paid = Column(Integer)
    nice_rating = Column(Integer)
    ordered_on = Column(DateTime, default=datetime.utcnow)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    alt_name = Column(String, default='')
    email = Column(String)
    password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    joined_on = Column(DateTime, default=datetime.utcnow)
