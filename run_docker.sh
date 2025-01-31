#!/bin/bash

# Название образа
IMAGE_NAME="telegram_bot_aiogram"

# Путь к директории с проектом
DOCKERFILE_DIR=$(pwd)/docker

# Строим Docker-образ
echo "Building Docker image..."
docker build --no-cache -t $IMAGE_NAME $PROJECT_DIR

# Проверяем, есть ли контейнер с таким именем
CONTAINER_NAME="telegram_bot_container"
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
  echo "Removing old container..."
  docker rm -f $CONTAINER_NAME
fi

# Запускаем контейнер
echo "Starting new container..."
docker run -d \
  --name $CONTAINER_NAME \
  --env-file .env \
  $IMAGE_NAME

