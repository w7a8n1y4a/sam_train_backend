from fastapi import APIRouter, UploadFile, Depends

from app.services.model_service import ModelService

router = APIRouter()


@router.post("", response_model=str)
def get_infer_image(file: UploadFile, model_service: ModelService = Depends()):
    return model_service.get_mask_link(file)
