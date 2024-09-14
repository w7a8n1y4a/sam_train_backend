import os
import shutil
import uuid as pkg_uuid

import fastapi
import urllib3

from typing import Union


import filetype

import numpy as np
import torch
from PIL import Image
from fastapi import UploadFile, HTTPException
from fastapi import status as http_status
from strawberry.file_uploads import Upload

from app import settings
from app.configs.minio import minio_client, bucket_name
from app.segment_anything import build_sam_vit_b, SamPredictor
from app.segment_anything.lora import LoRA_sam
from app.segment_anything.modeling import Sam


class ModelService:

    model: Sam = None

    def __init__(
        self,
    ) -> None:
        self.model = self.get_model()

    @staticmethod
    def get_model() -> Sam:
        device = "cuda" if torch.cuda.is_available() else "cpu"

        sam = build_sam_vit_b(checkpoint=f"./model/sam_vit_b_01ec64.pth")
        sam_lora = LoRA_sam(sam, 512)
        sam_lora.load_lora_parameters(f"./model/best.safetensors")

        model = sam_lora.sam

        model.eval()
        model.to(device)

        return model

    def mask_prediction(self, file: Union[UploadFile, Upload]) -> tuple[str, str]:
        
        self.is_valid_image_size(file)

        filename, extension, filepath = self.save_file_to_path(file)

        self.is_valid_image_extension(extension)

        image = np.array(Image.open(filepath).convert('L'))

        x_max, y_max = image.shape

        box = (0, 0, x_max, y_max)

        predictor = SamPredictor(self.model)
        predictor.set_image(image)

        masks, iou_pred, low_res_iou = predictor.predict(
            box=np.array(box),
            multimask_output=False,
        )

        mask = Image.fromarray(np.uint8(masks[0] * 255))

        uuid = pkg_uuid.uuid4()

        filename = f"{uuid}.png"
        filepath = f'{settings.app_path}/tmp/{filename}'

        mask.save(filepath)

        return filename, filepath

    def get_mask_link(self, file: Union[UploadFile, Upload]) -> str:

        filename, filepath = self.mask_prediction(file)

        minio_client.fput_object(bucket_name, filename, filepath)

        os.remove(filepath)

        file_url = minio_client.presigned_get_object(bucket_name, filename)

        return file_url

    def save_file_to_path(self, file: Union[UploadFile, Upload]) -> (str,):
        """Сохраняет файл, в tmp и отдаёт его имя, расширение и абсолютный путь"""

        # генерирует имя и путь до файла
        filepath_uuid_only = f"{os.path.abspath(os.getcwd())}/tmp/{str(pkg_uuid.uuid4())}"

        # первично записывает файл в бинарном виде
        with open(filepath_uuid_only, 'wb') as buffer:
            if isinstance(file, bytes):
                buffer.write(file)
            else:
                shutil.copyfileobj(file.file, buffer)

        # позволяет получить расширение файла из суперблока
        try:
            extension = filetype.guess(filepath_uuid_only).extension
        except AttributeError:
            extension = file.filename.split('.')[-1] if len(file.filename.split('.')) > 1 else None

        # генерирует конечное название и путь до файла
        filename = pkg_uuid.uuid4()
        filename_witch_extension = self.get_filename(str(filename), extension)
        filepath = f"{os.path.abspath(os.getcwd())}/tmp/{filename_witch_extension}"

        # копирует файл на полный путь с расширением
        with open(filepath_uuid_only, 'rb') as old_filepath, open(filepath, 'wb') as new_filepath:
            shutil.copyfileobj(old_filepath, new_filepath)

        # удаление первичного файла
        os.remove(filepath_uuid_only)

        return filename, extension, filepath

    @staticmethod
    def get_filename(filename: str, extension: str) -> str:
        """Создаёт имя файла из имени и расширения"""
        return f'{filename}{f".{extension}" if extension else ""}'

    @staticmethod
    def is_valid_image_size(file: Union[UploadFile, Upload]) -> None:
        """Проверяет, является ли расширение расширением фотокарточки"""

        if isinstance(file, bytes) and len(file) > 50 * 2**20:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Large File size for Telegram"
            )

        if type(file) in (UploadFile, Upload) and file.size > 50 * 2**20:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Large File size for Telegram"
            )

    @staticmethod
    def is_valid_image_extension(extension: str) -> bool:
        """Проверяет, является ли расширение расширением фотокарточки"""

        extensions = ['png', 'jpg', 'jpeg']

        if extension not in extensions:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Not valid extension. Valid: {str(extensions)}",
            )
