FROM python:3.12-slim

WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в /app
COPY . .

# Делаем entrypoint.sh исполняемым
RUN chmod +x entrypoint.sh

# Задаём entrypoint для обработки сигналов
ENTRYPOINT ["./entrypoint.sh"]
