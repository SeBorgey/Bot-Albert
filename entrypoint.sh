#!/usr/bin/env bash
set -e

# Функция, вызываемая при получении SIGTERM
cleanup() {
    echo "Получен SIGTERM, перезапускаем бота..."
    pkill -f main.py || true
    # Небольшая пауза перед перезапуском
    sleep 1
    python3 main.py &
}

# Устанавливаем trap на SIGTERM
trap 'cleanup' SIGTERM

# Запускаем бота
python3 main.py &

# Ждём завершения дочерних процессов
wait
