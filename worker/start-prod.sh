#!/bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

cd $SCRIPTPATH
echo $SCRIPTPATH
if [ ! -d "$SCRIPTPATH/env" ]
then
	echo "Creating Virtual Environment..."
	python3 -m venv env
fi
source env/bin/activate
pip3 install -r  ../docker/worker/requirements.txt

# export DO_ACCESS_KEY_ID="XXXX"
# export DO_SECRET_ACCESS_KEY="XXXX"
export PYTHONUNBUFFERED=0
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_DEFAULT_USER=rabbitmquser
export RABBITMQ_DEFAULT_PASS=pa55word
export S3_REGION_NAME=ams3
export S3_ENDPOINT_URI=https://ams3.digitaloceanspaces.com
export S3_BUCKET_NAME=swat1
export BACKUP_FILE_PATH=$SCRIPTPATH/../files
export LOG_DIR=$SCRIPTPATH/../logs

python -u worker.py