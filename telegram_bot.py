import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")


class TelegramBot:
    def __init__(self, storage):
        logging.debug("Initializing TelegramBot.")
        self.storage = storage
        self.discord_bot = None
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

        # Состояния пользователя: user_id -> {"action": "set_threshold"/"add_server"/"remove_server"/"bugreport"}
        self.user_states = {}

        # Главное меню с русскими кнопками в 2 ряда
        # Помощь, Настройки, Порог, Режим, Добавить, Удалить, Багрепорт
        self.main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Помощь"), KeyboardButton(text="Настройки")],
                [KeyboardButton(text="Порог"), KeyboardButton(text="Режим")],
                [KeyboardButton(text="Добавить"), KeyboardButton(text="Удалить")],
                [KeyboardButton(text="Багрепорт")]
            ],
            resize_keyboard=True
        )

        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            user_id = message.from_user.id
            logging.debug(f"Received /start from user_id={user_id}.")
            await self.handle_start_command(user_id)
            await message.answer(
                "Привет! Ниже есть меню с кнопками для управления ботом.\nИли используйте /help для списка команд.",
                reply_markup=self.main_keyboard
            )

        # Команда /help осталась, чтобы не ломать логику
        @self.dp.message(Command("help"))
        async def cmd_help(message: types.Message):
            user_id = message.from_user.id
            logging.debug(f"Received /help from user_id={user_id}.")
            help_text = (
                "Список команд:\n"
                "/help - показать это сообщение\n"
                "/setthreshold <число> - установить порог уведомления\n"
                "/setmode <total|max_channel> - установить режим подсчёта\n"
                "/addserver <server_id> - добавить сервер\n"
                "/removeserver <server_id> - убрать сервер\n"
                "/settings - показать текущие настройки\n"
                "/bugreport <текст> - отправить сообщение администратору\n\n"
                "Или используйте кнопки для взаимодействия."
            )
            await message.answer(help_text)

        # Команда /settings осталась
        @self.dp.message(Command("settings"))
        async def cmd_settings(message: types.Message):
            user_id = message.from_user.id
            logging.debug(f"Received /settings from user_id={user_id}.")
            await self.handle_settings_command(user_id, message)

        # Остальные команды изначальной логики остаются, чтобы не ломать существующий функционал:
        @self.dp.message(Command("setthreshold"))
        async def cmd_setthreshold(message: types.Message):
            logging.debug(f"Received /setthreshold from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split(maxsplit=1)
            if len(parts) < 2:
                await message.answer("Укажи threshold")
                return
            threshold_str = parts[1]
            if not threshold_str.isdigit():
                await message.answer("Порог должен быть числом.")
                return
            threshold = int(threshold_str)
            await self.handle_set_threshold_command(user_id, threshold)
            await message.answer("Порог установлен.")

        @self.dp.message(Command("setmode"))
        async def cmd_setmode(message: types.Message):
            logging.debug(f"Received /setmode from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split(maxsplit=1)
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
            parts = message.text.strip().split(maxsplit=1)
            if len(parts) < 2:
                await message.answer("Укажи server_id")
                return
            server_str = parts[1]
            if not server_str.isdigit():
                await message.answer("server_id должен быть числом.")
                return
            server_id = int(server_str)
            await self.handle_add_server_command(user_id, server_id)
            await message.answer("Сервер добавлен.")

        @self.dp.message(Command("removeserver"))
        async def cmd_removeserver(message: types.Message):
            logging.debug(f"Received /removeserver from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split(maxsplit=1)
            if len(parts) < 2:
                await message.answer("Укажи server_id")
                return
            server_str = parts[1]
            if not server_str.isdigit():
                await message.answer("server_id должен быть числом.")
                return
            server_id = int(server_str)
            await self.handle_remove_server_command(user_id, server_id)
            await message.answer("Сервер удален.")

        @self.dp.message(Command("bugreport"))
        async def cmd_bugreport(message: types.Message):
            # Формат: /bugreport <текст>
            logging.debug(f"Received /bugreport from user_id={message.from_user.id}.")
            user_id = message.from_user.id
            parts = message.text.strip().split(maxsplit=1)
            if len(parts) < 2:
                await message.answer("Укажи текст багрепорта после команды /bugreport")
                return
            report_text = parts[1]
            await self.handle_bugreport_command(user_id, report_text, message)

        # Обработка нажатий на кнопки без слеш-команд:
        @self.dp.message(F.text == "Помощь")
        async def btn_help(message: types.Message):
            # Показываем то же, что и /help
            await cmd_help(message)

        @self.dp.message(F.text == "Настройки")
        async def btn_settings(message: types.Message):
            await cmd_settings(message)

        @self.dp.message(F.text == "Порог")
        async def btn_threshold(message: types.Message):
            user_id = message.from_user.id
            await message.answer("Введите новый порог (число):")
            self.user_states[user_id] = {"action": "set_threshold"}

        @self.dp.message(F.text == "Режим")
        async def btn_mode(message: types.Message):
            user_id = message.from_user.id
            # Показываем inline-клавиатуру для выбора режима
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Суммарно (total)", callback_data="mode_total")],
                [InlineKeyboardButton(text="Макс. канал (max_channel)", callback_data="mode_max")]
            ])
            await message.answer("Выберите режим:", reply_markup=inline_kb)

        @self.dp.callback_query()
        async def callback_mode(call: types.CallbackQuery):
            user_id = call.from_user.id
            if call.data == "mode_total":
                await self.handle_set_mode_command(user_id, "total")
                await call.message.edit_text("Режим обновлен на total.")
            elif call.data == "mode_max":
                await self.handle_set_mode_command(user_id, "max_channel")
                await call.message.edit_text("Режим обновлен на max_channel.")
            await call.answer()

        @self.dp.message(F.text == "Добавить")
        async def btn_add_server(message: types.Message):
            user_id = message.from_user.id
            await message.answer("Введите ID сервера (число):")
            self.user_states[user_id] = {"action": "add_server"}

        @self.dp.message(F.text == "Удалить")
        async def btn_remove_server(message: types.Message):
            user_id = message.from_user.id
            await message.answer("Введите ID сервера (число):")
            self.user_states[user_id] = {"action": "remove_server"}

        @self.dp.message(F.text == "Багрепорт")
        async def btn_bugreport_button(message: types.Message):
            user_id = message.from_user.id
            await message.answer("Опишите проблему:")
            self.user_states[user_id] = {"action": "bugreport"}

        # Обработчик остальных сообщений - когда ждём ответа от пользователя
        @self.dp.message()
        async def catch_all(message: types.Message):
            user_id = message.from_user.id
            user_state = self.user_states.get(user_id, {})
            action = user_state.get("action")

            if action == "set_threshold":
                if not message.text.isdigit():
                    await message.answer("Порог должен быть числом. Попробуйте ещё раз.")
                    return
                threshold = int(message.text)
                await self.handle_set_threshold_command(user_id, threshold)
                await message.answer(f"Порог установлен на {threshold}.")
                self.user_states[user_id] = {}

            elif action == "add_server":
                if not message.text.isdigit():
                    await message.answer("ID сервера должен быть числом.")
                    return
                server_id = int(message.text)
                await self.handle_add_server_command(user_id, server_id)
                await message.answer(f"Сервер {server_id} добавлен.")
                self.user_states[user_id] = {}

            elif action == "remove_server":
                if not message.text.isdigit():
                    await message.answer("ID сервера должен быть числом.")
                    return
                server_id = int(message.text)
                await self.handle_remove_server_command(user_id, server_id)
                await message.answer(f"Сервер {server_id} удален.")
                self.user_states[user_id] = {}

            elif action == "bugreport":
                report_text = message.text.strip()
                await self.handle_bugreport_command(user_id, report_text, message)
                self.user_states[user_id] = {}

            else:
                # Нет активного действия - можно ответить подсказкой
                await message.answer("Используйте меню или /help для просмотра команд.")

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

        if servers:
            servers_str = "\n".join(
                f"- {self.discord_bot.client.get_guild(s_id).name} (ID: {s_id})"
                for s_id in servers
            )
        else:
            servers_str = "нет"

        text = (
            f"Текущие настройки:\n"
            f"Отслеживаемые сервера:\n{servers_str}\n"
            f"Порог: {threshold}\n"
            f"Режим: {mode}\n"
        )
        await message.answer(text)

    async def handle_bugreport_command(self, user_id, report_text, message: types.Message):
        logging.debug(f"Handling bugreport from user_id={user_id}.")
        if not TELEGRAM_ADMIN_ID:
            await message.answer("Администратор не настроен. Сообщение не отправлено.")
            return
        admin_id = int(TELEGRAM_ADMIN_ID)
        report_msg = f"Bugreport from user_id={user_id}:\n{report_text}"
        await self.bot.send_message(admin_id, report_msg)
        await message.answer("Спасибо за ваш отзыв! Ваш багрепорт отправлен администратору.")

    def notify_user(self, user_id, channel_name, user_count, user_list):
        logging.debug(f"Notifying user_id={user_id} about channel={channel_name}, count={user_count}.")
        text = f"На {channel_name} собралось {user_count} человек: {', '.join(user_list)}"
        asyncio.create_task(self.bot.send_message(user_id, text))
