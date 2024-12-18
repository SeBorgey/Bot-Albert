import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class TelegramBot:
    def __init__(self, storage):
        logging.debug("Initializing TelegramBot.")
        self.storage = storage
        self.discord_bot = None
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            logging.debug(f"Received /start from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            await self.handle_start_command(user_id)
            await message.answer("Привет! Используй /help чтобы увидеть доступные команды.")

        @self.dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            logging.debug(f"Received /help from user_id={message.from_user.id}.")
            help_text = (
                "Список команд:\n"
                "/help - показать это сообщение\n"
                "/setthreshold <число> - установить порог уведомления\n"
                "/setmode <total|max_channel> - установить режим подсчёта\n"
                "/addserver <server_id> - добавить сервер для отслеживания\n"
                "/removeserver <server_id> - убрать сервер из отслеживания\n"
                "/settings - показать текущие настройки\n"
            )
            await message.answer(help_text)

        @self.dp.message(Command("setthreshold"))
        async def cmd_setthreshold(message: types.Message):
            logging.debug(f"Received /setthreshold from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи threshold")
                return
            threshold = int(parts[1])
            await self.handle_set_threshold_command(user_id, threshold)
            await message.answer("Порог установлен.")

        @self.dp.message(Command("setmode"))
        async def cmd_setmode(message: types.Message):
            logging.debug(f"Received /setmode from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи режим: total или max_channel")
                return
            mode = parts[1]
            if mode not in ["total", "max_channel"]:
                await message.answer("Неверный режим.")
                return
            await self.handle_set_mode_command(user_id, mode)
            await message.answer("Режим обновлен.")

        @self.dp.message(Command("addserver"))
        async def cmd_addserver(message: types.Message):
            logging.debug(f"Received /addserver from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи server_id")
                return
            server_id = int(parts[1])
            await self.handle_add_server_command(user_id, server_id)
            await message.answer("Сервер добавлен.")

        @self.dp.message(Command("removeserver"))
        async def cmd_removeserver(message: types.Message):
            logging.debug(f"Received /removeserver from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи server_id")
                return
            server_id = int(parts[1])
            await self.handle_remove_server_command(user_id, server_id)
            await message.answer("Сервер удален.")

        @self.dp.message(Command("settings"))
        async def cmd_settings(message: types.Message):
            logging.debug(f"Received /settings from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            await self.handle_settings_command(user_id, message)

    def set_discord_bot(self, discord_bot):
        logging.debug("Setting discord bot in TelegramBot.")
        self.discord_bot = discord_bot

    async def start_async(self):
        logging.debug("Running TelegramBot polling.")
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    async def handle_start_command(self, user_id):
        logging.debug(f"Handling start command for user_id={user_id}.")
        settings = self.storage.get_user_settings(user_id)
        if not settings:
            self.storage.update_user_settings(user_id, {
                "servers": [],
                "threshold": 0,
                "mode": "total"
            })

    async def handle_set_threshold_command(self, user_id, threshold):
        logging.debug(f"Handling setthreshold for user_id={user_id}, threshold={threshold}.")
        settings = self.storage.get_user_settings(user_id) or {
            "servers": [],
            "threshold": 0,
            "mode": "total"
        }
        settings["threshold"] = threshold
        self.storage.update_user_settings(user_id, settings)

    async def handle_set_mode_command(self, user_id, mode):
        logging.debug(f"Handling setmode for user_id={user_id}, mode={mode}.")
        settings = self.storage.get_user_settings(user_id) or {
            "servers": [],
            "threshold": 0,
            "mode": "total"
        }
        settings["mode"] = mode
        self.storage.update_user_settings(user_id, settings)

    async def handle_add_server_command(self, user_id, server_id):
        logging.debug(f"Handling addserver for user_id={user_id}, server_id={server_id}.")
        settings = self.storage.get_user_settings(user_id) or {
            "servers": [],
            "threshold": 0,
            "mode": "total"
        }
        servers = settings.get("servers", [])
        if server_id not in servers:
            servers.append(server_id)
        settings["servers"] = servers
        self.storage.update_user_settings(user_id, settings)

    async def handle_remove_server_command(self, user_id, server_id):
        logging.debug(f"Handling removeserver for user_id={user_id}, server_id={server_id}.")
        settings = self.storage.get_user_settings(user_id) or {
            "servers": [],
            "threshold": 0,
            "mode": "total"
        }
        servers = settings.get("servers", [])
        if server_id in servers:
            servers.remove(server_id)
        settings["servers"] = servers
        self.storage.update_user_settings(user_id, settings)

    async def handle_settings_command(self, user_id, message: types.Message):
        logging.debug(f"Handling settings for user_id={user_id}.")
        settings = self.storage.get_user_settings(user_id)
        if not settings:
            await message.answer("У вас нет настроек. Используйте /start для инициализации.")
            return
        servers = settings.get("servers", [])
        threshold = settings.get("threshold", 0)
        mode = settings.get("mode", "total")
        text = (
            f"Текущие настройки:\n"
            f"Отслеживаемые сервера: {', '.join(map(str, servers)) if servers else 'нет'}\n"
            f"Порог: {threshold}\n"
            f"Режим: {mode}\n"
        )
        await message.answer(text)

    def notify_user(self, user_id, channel_name, user_count, user_list):
        logging.debug(f"Notifying user_id={user_id} about channel={channel_name}, count={user_count}.")
        text = f"На {channel_name} собралось {user_count} человек: {', '.join(user_list)}"
        asyncio.create_task(self.bot.send_message(user_id, text))
