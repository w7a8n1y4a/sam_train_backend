from strawberry.tools import create_type

from app.schemas.gql.mutations.model import *

Mutation = create_type(
    "Mutation",
    [gen_image],
)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"
