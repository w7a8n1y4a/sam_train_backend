from functools import wraps

import uvicorn

from fastapi import FastAPI
from telebot import types
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

from app import settings
from app.configs.bot import tbot
from app.routers.v1.endpoints import api_router
from app.configs.gql import get_graphql_context
from app.schemas.gql.mutation import Mutation, Query
from app.schemas.pydantic.shared import Root

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f'{settings.app_prefix}{settings.api_v1_prefix}/openapi.json',
    docs_url=f'{settings.app_prefix}/docs',
    debug=settings.debug,
)


# GraphQL Schema and Application Instance
schema = Schema(query=Query, mutation=Mutation)
graphql = GraphQLRouter(
    schema,
    graphiql=True,
    context_getter=get_graphql_context,
)

# Integrate GraphQL Application to the Core one
app.include_router(
    graphql,
    prefix=f'{settings.app_prefix}/graphql',
    include_in_schema=False,
)


@app.get(f'{settings.app_prefix}', response_model=Root, tags=['status'])
def root():
    return {
        'name': settings.project_name,
        'version': settings.version,
        'description': settings.description,
        'swagger': f'{settings.app_prefix}/docs',
        'graphql': f'{settings.app_prefix}/graphql',
    }


@app.post(f"{settings.app_prefix}/bot")
def webhook(update: dict):
    """Вебхук до телеги"""

    if update:
        update = types.Update.de_json(update)
        tbot.process_new_updates([update])
        return {"status": "true"}
    else:
        return


app.include_router(api_router, prefix=f'{settings.app_prefix}{settings.api_v1_prefix}')

if __name__ == '__main__':
    uvicorn.run('app.main:app', port=8080, host='0.0.0.0', reload=True)
