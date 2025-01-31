# Название образа
$imageName = "telegram_bot_aiogram"

# Путь к директории с проектом
$projectDir = (Get-Location).Path

# Строим Docker-образ
Write-Host "Building Docker image..."
docker build -t $imageName $projectDir

# Название контейнера
$containerName = "telegram_bot_container"

# Проверяем, есть ли контейнер с таким именем
if (docker ps -a -q -f "name=$containerName") {
    Write-Host "Removing old container..."
    docker rm -f $containerName
}

# Запускаем контейнер
Write-Host "Starting new container..."
docker run -d `
  --name $containerName `
  --env-file .env `
  $imageName

Write-Host "Container $containerName is running."
