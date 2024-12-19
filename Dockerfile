FROM python:3.12-slim

WORKDIR /app

# Устанавливаем необходимые пакеты, включая psmisc для pkill
RUN apt-get update && apt-get install -y --no-install-recommends build-essential psmisc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
