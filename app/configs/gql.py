from fastapi import Depends
from strawberry.types import Info

from app.services.model_service import ModelService


async def get_graphql_context(model_service: ModelService = Depends()):
    return {'model_service': model_service}


def get_model_service(info: Info) -> ModelService:
    return info.context['model_service']
