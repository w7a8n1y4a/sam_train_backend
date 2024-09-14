import pika


# Функция для подключения к RabbitMQ
def get_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_processing_queue', durable=True)
    return channel

channel = get_rabbitmq_connection()

filenames = ['1.png', '2.png', '3.png']

for filename in filenames:
    channel.basic_publish(
        exchange='',
        routing_key='image_processing_queue',
        body=filename,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сделать сообщение "устойчивым"
        )
    )
