import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # загрузка переменных окружения из .env

ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"

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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')
    logging.debug("Starting main.")
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
