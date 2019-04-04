#!/bin/bash
echo Waiting for RabbitMQ
while ! nc -z rabbitmq 5672; do sleep 3; done
echo Starting Worker
nodemon --exec "python -u" /app/worker.py