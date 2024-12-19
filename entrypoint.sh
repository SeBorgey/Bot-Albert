#!/usr/bin/env bash
set -e

BOT_CMD="python3 main.py"

# Запускаем бота в фоне и сохраняем его PID
$BOT_CMD &
BOT_PID=$!

cleanup() {
    echo "Получен SIGTERM, перезапускаем бота..."
    # Принудительно убиваем старый процесс бота
    kill -9 $BOT_PID || true
    sleep 2
    # Запускаем бота снова
    $BOT_CMD &
    BOT_PID=$!
}

trap 'cleanup' SIGTERM

# Ожидаем завершения процессов
wait
