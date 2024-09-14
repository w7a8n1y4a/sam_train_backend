from functools import wraps
import logging
from minio.error import S3Error

import pika
import threading
from fastapi import FastAPI

import uvicorn

from fastapi import FastAPI
from telebot import types
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

from app import settings
from app.routers.v1.endpoints import api_router
from app.configs.gql import get_graphql_context
from app.schemas.gql.mutation import Mutation, Query
from app.schemas.pydantic.shared import Root
from app.configs.minio import minio_client, bucket_name
from app.schemas.bot.bot import *

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


def process_image(filename: str):

    try:
        target_file = minio_client.get_object(bucket_name, filename)
    except S3Error as err:
        logging.exception(err.message)
        return

    model_service = ModelService()
    filename, filepath = model_service.mask_prediction(target_file.data)

    minio_client.fput_object(bucket_name, filename, filepath)
    os.remove(filepath)

    logging.info(f'New mask name in minio: {filename}')


# Функция для подключения к RabbitMQ и получения сообщений
def consume_images():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_processing_queue', durable=True)

    # Callback функция обработки сообщения
    def callback(ch, method, properties, body):
        filename = body.decode('utf-8')
        process_image(filename)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем обработку

    # Настройка QoS, чтобы получать только одно сообщение за раз
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='image_processing_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def start_consumer_thread():
    consumer_thread = threading.Thread(target=consume_images)
    consumer_thread.daemon = True
    consumer_thread.start()

@app.on_event("startup")
def startup_event():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    start_consumer_thread()


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
