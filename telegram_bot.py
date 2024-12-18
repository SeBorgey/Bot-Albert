import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN

class TelegramBot:
    def __init__(self, storage):
        self.storage = storage
        self.discord_bot = None
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            user_id = message.from_user.id
            await self.handle_start_command(user_id)
            await message.answer("Привет. Укажи сервер для отслеживания с помощью /setserver <server_id>")

        @self.dp.message(Command("setserver"))
        async def cmd_setserver(message: types.Message):
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи server_id")
                return
            server_id = int(parts[1])
            await self.handle_set_server_command(user_id, server_id)
            await message.answer("Сервер установлен. Проверь, что бот находится на нем и имеет права.")

        @self.dp.message(Command("setthreshold"))
        async def cmd_setthreshold(message: types.Message):
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

        @self.dp.message(Command("addchannel"))
        async def cmd_addchannel(message: types.Message):
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи channel_id")
                return
            channel_id = int(parts[1])
            await self.handle_add_channel_command(user_id, channel_id)
            await message.answer("Канал добавлен.")

        @self.dp.message(Command("removechannel"))
        async def cmd_removechannel(message: types.Message):
            user_id = message.from_user.id
            parts = message.text.strip().split()
            if len(parts) < 2:
                await message.answer("Укажи channel_id")
                return
            channel_id = int(parts[1])
            await self.handle_remove_channel_command(user_id, channel_id)
            await message.answer("Канал удален.")

    def set_discord_bot(self, discord_bot):
        self.discord_bot = discord_bot

    def start(self):
        asyncio.run(self._start_polling())

    async def _start_polling(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    async def handle_start_command(self, user_id):
        settings = self.storage.get_user_settings(user_id)
        if not settings:
            self.storage.update_user_settings(user_id, {
                "server_id": None,
                "threshold": 0,
                "mode": "total",
                "channels": []
            })

    async def handle_set_server_command(self, user_id, server_id):
        settings = self.storage.get_user_settings(user_id) or {}
        settings["server_id"] = server_id
        self.storage.update_user_settings(user_id, settings)

    async def handle_set_threshold_command(self, user_id, threshold):
        settings = self.storage.get_user_settings(user_id) or {}
        settings["threshold"] = threshold
        self.storage.update_user_settings(user_id, settings)

    async def handle_set_mode_command(self, user_id, mode):
        settings = self.storage.get_user_settings(user_id) or {}
        settings["mode"] = mode
        self.storage.update_user_settings(user_id, settings)

    async def handle_add_channel_command(self, user_id, channel_id):
        settings = self.storage.get_user_settings(user_id) or {}
        ch = settings.get("channels", [])
        if channel_id not in ch:
            ch.append(channel_id)
        settings["channels"] = ch
        self.storage.update_user_settings(user_id, settings)

    async def handle_remove_channel_command(self, user_id, channel_id):
        settings = self.storage.get_user_settings(user_id) or {}
        ch = settings.get("channels", [])
        if channel_id in ch:
            ch.remove(channel_id)
        settings["channels"] = ch
        self.storage.update_user_settings(user_id, settings)

    def notify_user(self, user_id, channel_name, user_count, user_list):
        text = f"На канале {channel_name} собралось {user_count} человек: {', '.join(user_list)}"
        asyncio.create_task(self.bot.send_message(user_id, text))
