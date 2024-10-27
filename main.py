from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from items_views import router as items_router
from api_v1 import router as router_v1
from core.models import Base, db_helper
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # `create_all`  без скобок ()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(items_router)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


@app.get("/")
def hello_index():
    return {"message": "Hello, index!"}


@app.get("/hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, log_level="info", reload=False)
