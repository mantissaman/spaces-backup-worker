#!/bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

cd $SCRIPTPATH
echo $SCRIPTPATH
rm /certs/cv_jwt_rsa
rm /certs/cv_jwt_rsa.pub

ssh-keygen -t rsa -f /certs/cv_jwt_rsa -q -P ""

echo Waiting for RabbitMQ
while ! nc -z rabbitmq 5672; do sleep 3; done
echo Starting API
python -m flask run --host=0.0.0.0