import asyncio
import logging
import os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()  # загрузка переменных окружения из .env

ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
LOGGING_TARGET = os.getenv("LOGGING_TARGET", "stdout")  # "file", "stdout", "both"
LOG_FILE_MAX_BYTES = int(os.getenv("LOG_FILE_MAX_BYTES", "1048576"))  # 1 MB
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "bot.log")  # Если нужно переопределить имя файла
# Количество резервных копий всегда одна
LOG_FILE_BACKUP_COUNT = 1

from telegram_bot import TelegramBot
from discord_bot import DiscordBot
from storage import Storage

async def main_async():
    storage = Storage()
    telegram_bot = TelegramBot(storage)
    discord_bot = DiscordBot(storage)
    telegram_bot.set_discord_bot(discord_bot)
    discord_bot.set_telegram_bot(telegram_bot)

    await asyncio.gather(
        telegram_bot.start_async(),
        discord_bot.start_async()
    )

def main():
    if ENABLE_LOGGING:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Удаляем все существующие хэндлеры
    while logger.handlers:
        logger.handlers.pop()

    # Настраиваем хэндлеры в зависимости от LOGGING_TARGET
    if LOGGING_TARGET in ("stdout", "both"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(console_handler)

    if LOGGING_TARGET in ("file", "both"):
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(file_handler)

    # Подавляем предупреждения от discord
    logging.getLogger('discord').setLevel(logging.ERROR)

    logging.debug("Starting main.")
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
