import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from app.configs.gql import get_model_service


@strawberry.mutation
def gen_image(info: Info, file: Upload) -> str:
    model_service = get_model_service(info)
    return model_service.get_mask_link(file)
