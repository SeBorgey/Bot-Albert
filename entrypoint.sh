#!/usr/bin/env bash
set -e

BOT_CMD="python3 main.py"

# Запускаем бота в фоне и сохраняем его PID
$BOT_CMD &
BOT_PID=$!

cleanup() {
    echo "Получен SIGTERM, перезапускаем бота..."
    # Останавливаем предыдущий процесс бота по PID
    kill $BOT_PID || true
    sleep 1
    # Запускаем бота снова
    $BOT_CMD &
    BOT_PID=$!
}

trap 'cleanup' SIGTERM

# Ожидаем завершения процессов
wait
