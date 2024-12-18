# main.py
from telegram_bot import TelegramBot
from discord_bot import DiscordBot
from storage import Storage

def main():
    storage = Storage()
    telegram_bot = TelegramBot(storage)
    discord_bot = DiscordBot(storage)
    telegram_bot.set_discord_bot(discord_bot)
    discord_bot.set_telegram_bot(telegram_bot)
    telegram_bot.start()
    discord_bot.start()

if __name__ == '__main__':
    main()
