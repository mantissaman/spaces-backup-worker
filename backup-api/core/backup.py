import os
import pika
import logging
import logging.config


RABBITMQ_DEFAULT_USER = os.environ['RABBITMQ_DEFAULT_USER']
RABBITMQ_DEFAULT_PASS = os.environ['RABBITMQ_DEFAULT_PASS']
RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
RABBITMQ_PORT = int(os.environ['RABBITMQ_PORT'])

credentials = pika.PlainCredentials(
    RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                       port=RABBITMQ_PORT,
                                       credentials=credentials)


class Backup:
    def __init__(self, logger_conf):
        logging.config.dictConfig(logger_conf.get_logger_config())
        self.logger = logging.getLogger(__name__)


    def enqueue(self, message):
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='spaces_backup_queue', durable=True)
        channel.basic_publish(
        exchange='',
        routing_key='spaces_backup_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
        print(" [x] Sent %r" % message)
        connection.close()