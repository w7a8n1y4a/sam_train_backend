from fastapi import APIRouter

from app.routers.v1.model_router import router as model_router

api_router = APIRouter()

include_api = api_router.include_router

routers = ((model_router, "models", "models"),)

for router, prefix, tag in routers:
    if tag:
        include_api(router, prefix=f"/{prefix}", tags=[tag])
    else:
        include_api(router, prefix=f"/{prefix}")
