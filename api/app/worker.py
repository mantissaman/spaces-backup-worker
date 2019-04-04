import pika
import os
import json
import boto3
import io
import logging
import logging.config
import yaml

dirname = os.path.dirname(__file__)

RABBITMQ_DEFAULT_USER = os.environ['RABBITMQ_DEFAULT_USER']
RABBITMQ_DEFAULT_PASS = os.environ['RABBITMQ_DEFAULT_PASS']
RABBITMQ_HOST = os.environ['RABBITMQ_HOST']
RABBITMQ_PORT = int(os.environ['RABBITMQ_PORT'])
S3_REGION_NAME = os.environ['S3_REGION_NAME']
S3_ENDPOINT_URI = os.environ['S3_ENDPOINT_URI']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
DO_ACCESS_KEY_ID = os.environ['DO_ACCESS_KEY_ID']
DO_SECRET_ACCESS_KEY = os.environ['DO_SECRET_ACCESS_KEY']
BACKUP_FILE_PATH = os.environ['BACKUP_FILE_PATH']
LOG_DIR = os.environ['LOG_DIR']

with open(os.path.join(dirname, 'logging.yaml'), 'r') as f:
    config = yaml.safe_load(f.read())
    info_file = config['handlers']['info_file_handler']['filename']
    error_file = config['handlers']['error_file_handler']['filename']
    config['handlers']['info_file_handler']['filename']=os.path.join(LOG_DIR, info_file)
    config['handlers']['error_file_handler']['filename']=os.path.join(LOG_DIR, error_file)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

credentials = pika.PlainCredentials(
    RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST,
                                       port=RABBITMQ_PORT,
                                       credentials=credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()


channel.queue_declare(queue='spaces_backup_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

s3 = boto3.client('s3',
                  region_name=S3_REGION_NAME,
                  endpoint_url=S3_ENDPOINT_URI,
                  aws_access_key_id=DO_ACCESS_KEY_ID,
                  aws_secret_access_key=DO_SECRET_ACCESS_KEY)

#filename is Key


def download_file(file_name):
    try:
        obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file_name)
        with open(os.path.join(BACKUP_FILE_PATH, file_name), 'wb') as filedesciptor:
            buffer = json.loads(obj['Body'].read())
            data = buffer['data']
            filedesciptor.write(bytes(data))
    except Exception as e:
        logger.error("Unexpected error: %s" % e, exc_info=True)


def delete_file(file_name):
    try:
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=file_name)
    except Exception as e:
        logger.error("Unexpected error: %s" % e, exc_info=True)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        logger.info(
            f"Received {data['operation']} operation for file {data['file_name']}")

        if data['operation'] == "DOWNLOAD":
            download_file(data['file_name'])
        elif data['operation'] == "DELETE":
            delete_file(data['file_name'])
        else:
            logger.warn("Unknown Operation")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(
            f"Completed {data['operation']} operation for file {data['file_name']}")
    except Exception as e:
        logger.error("Unexpected error: %s" % e, exc_info=True)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='spaces_backup_queue', on_message_callback=callback)

channel.start_consuming()
