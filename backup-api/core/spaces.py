import os
import boto3
import json
import logging
import logging.config
from .backup import Backup

S3_REGION_NAME = os.environ['S3_REGION_NAME']
S3_ENDPOINT_URI = os.environ['S3_ENDPOINT_URI']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
DO_ACCESS_KEY_ID = os.environ['DO_ACCESS_KEY_ID']
DO_SECRET_ACCESS_KEY = os.environ['DO_SECRET_ACCESS_KEY']

s3 = boto3.client('s3',
                region_name=S3_REGION_NAME,
                endpoint_url=S3_ENDPOINT_URI,
                aws_access_key_id=DO_ACCESS_KEY_ID,
                aws_secret_access_key=DO_SECRET_ACCESS_KEY)

class Spaces:
    def __init__(self, logger_conf):
        logging.config.dictConfig(logger_conf.get_logger_config())
        self.logger = logging.getLogger(__name__)
        self.backup = Backup(logger_conf)

    def upload_file(self, file):
        try:
            s3.upload_fileobj(file, Bucket=S3_BUCKET_NAME, Key=file.filename)
            self.backup.enqueue(json.dumps({'operation':'DOWNLOAD', 'file_name': file.filename}, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            self.logger.error("Unexpected error: %s" % e, exc_info=True)

    def get_file(self, key):
        try:
            s3_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
            body = s3_object['Body']
            return body.read()
        except Exception as e:
            self.logger.error("Unexpected error: %s" % e, exc_info=True)
    def delete_file(self, file_name):
        try:
            s3.delete_object(Bucket=S3_BUCKET_NAME, Key=file_name)
            self.backup.enqueue(json.dumps({'operation':'DELETE', 'file_name': file_name}, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            logger.error("Unexpected error: %s" % e, exc_info=True)