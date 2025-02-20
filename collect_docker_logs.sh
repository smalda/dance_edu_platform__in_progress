#!/bin/bash

# Create docker_logs directory if it doesn't exist
mkdir -p docker_logs

# Set the path to docker-compose.yml
COMPOSE_FILE="docker/docker-compose.yml"

# Get logs for each service
docker compose -f $COMPOSE_FILE logs api > docker_logs/api.log
docker compose -f $COMPOSE_FILE logs consumer > docker_logs/consumer.log
docker compose -f $COMPOSE_FILE logs db > docker_logs/db.log
docker compose -f $COMPOSE_FILE logs rabbitmq > docker_logs/rabbitmq.log
docker compose -f $COMPOSE_FILE logs bot > docker_logs/bot.log

echo "Logs have been collected in docker_logs directory"
