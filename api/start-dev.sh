#!/bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

cd $SCRIPTPATH
echo $SCRIPTPATH

echo Waiting for RabbitMQ
while ! nc -z rabbitmq 5672; do sleep 3; done
echo Starting API
python -m flask run --host=0.0.0.0