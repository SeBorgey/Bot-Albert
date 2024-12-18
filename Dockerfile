FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы (при необходимости)
# Например, для установки PyNaCl могут понадобиться build-essential, libsodium-dev
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# При необходимости можно выставить переменные окружения через ENV или ARG
# ENV ENABLE_LOGGING=true
# ENV LOGGING_TARGET=both

# Запускаем скрипт
CMD ["python", "main.py"]
