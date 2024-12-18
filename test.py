from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TELEGRAM_BOT_TOKEN = "6832477390:AAE-DnGXPYO5DEUVLcS_EfQHk1hBY6EWGBk"

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="/help"), KeyboardButton(text="/settings")]
            ],
            resize_keyboard=True
        )
        await message.answer("Привет! Вот клавиатура:", reply_markup=keyboard)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
