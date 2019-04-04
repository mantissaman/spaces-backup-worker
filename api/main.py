from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
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
LOG_DIR = os.environ['LOG_DIR']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'xlsx', 'docx', 'jpeg', 'gif'])

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

s3 = boto3.client('s3',
                region_name=S3_REGION_NAME,
                endpoint_url=S3_ENDPOINT_URI,
                aws_access_key_id=DO_ACCESS_KEY_ID,
                aws_secret_access_key=DO_SECRET_ACCESS_KEY)

def backup(message):
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

def upload_file(file):
    try:
        s3.upload_fileobj(file, Bucket=S3_BUCKET_NAME, Key=file.filename)
        backup(json.dumps({'operation':'DOWNLOAD', 'file_name': file.filename}, ensure_ascii=False).encode('utf8'))
    except Exception as e:
        logger.error("Unexpected error: %s" % e, exc_info=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, instance_relative_config=True)

@app.route("/", methods=['GET', 'POST'])
def index():
    print("*****************")
    if request.method == 'POST':
        # There is no file selected to upload
        if "user_file" not in request.files:
            return "No user_file key in request.files"

        file = request.files["user_file"]

        # There is no file selected to upload
        if file.filename == "":
            return "Please select a file"

        # File is selected, upload to S3 and show S3 URL
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = upload_file(file)
            return str(output)
    else:
        return render_template("index.html")