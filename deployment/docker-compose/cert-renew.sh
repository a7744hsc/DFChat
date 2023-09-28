#!/bin/bash

COMPOSE="/snap/bin/docker-compose --no-ansi"
DOCKER="/snap/bin/docker"

cd /home/azureuser/dfchat/deploy/
$COMPOSE run certbot renew && $COMPOSE kill -s SIGHUP dfchat-nginx
$DOCKER system prune -af