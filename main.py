from fastapi import FastAPI
import uvicorn


import models
from database import engine
from routers import items, auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
