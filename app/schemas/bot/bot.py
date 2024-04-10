import os
import uuid as pkg_uuid
from io import BytesIO

from PIL import Image
from fastapi import UploadFile
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import settings
from app.configs.bot import tbot
from app.schemas.bot.enum import CommandNames
from app.services.model_service import ModelService


@tbot.message_handler(commands=[CommandNames.START.value, CommandNames.HELP.value])
def create_user_resolver(message):

    documentation = (
        '*Предсказание*\n'
        '/predict - получает на вход картинку и даёт предсказание\n'
        '\n'
        '*Управление*\n'
        '/start - запуск бота\n'
        '\n'
        '*Информация*\n'
        f'Название модели в MLFlow: {settings.model_id}'
    )

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Репозиторий разработки", url="https://git.pepemoss.com/universitat/ml/sam_train_backend"),
        InlineKeyboardButton("Репозиторий моделей", url="https://git.pepemoss.com/universitat/ml/sam_train"),
        InlineKeyboardButton("Open Api", url="https://pepemoss.com/sam_lora_backend/docs"),
        InlineKeyboardButton("Graphiql", url="https://pepemoss.com/sam_lora_backend/graphql"),
    )

    tbot.send_message(message.chat.id, text=documentation, reply_markup=markup, parse_mode='Markdown')


@tbot.message_handler(commands=[CommandNames.PREDICT.value])
def predict_mask_resolver(message):
    """Позволяет предсказать маску"""

    send = tbot.send_message(
        message.chat.id, f'Отправьте фотокарточку как документ, размер до 20 МБ', parse_mode='Markdown'
    )
    tbot.register_next_step_handler(send, handler_set_path)


class StarletteUploadFile:
    pass


def handler_set_path(call) -> None:

    if call.content_type == 'photo':
        downloaded_file = tbot.download_file(tbot.get_file(call.photo[0].file_id).file_path)
    elif call.content_type == 'document':
        downloaded_file = tbot.download_file(tbot.get_file(call.document.file_id).file_path)
    else:
        tbot.send_message(call.chat.id, f'Некорректный тип сообщения', parse_mode='Markdown')
        return None

    model_service = ModelService()

    filename, filepath = model_service.mask_prediction(
        UploadFile(BytesIO(downloaded_file), size=len(downloaded_file), filename='aboba.png')
    )

    image = Image.open(filepath)

    image = image.resize((1024, 1024))

    image.save(filepath)

    tbot.send_photo(call.chat.id, open(filepath, 'rb'))

    os.remove(filepath)
