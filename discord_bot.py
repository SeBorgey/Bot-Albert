import asyncio
import discord
import logging
from config import DISCORD_BOT_TOKEN

class DiscordBot:
    def __init__(self, storage):
        logging.debug("Initializing DiscordBot.")
        self.storage = storage
        self.telegram_bot = None
        self.client = discord.Client(intents=discord.Intents(guilds=True, voice_states=True, members=True))
        self.initialized = False
        self.tracked_data = {}  # (user_id, guild_id) -> last_count

        @self.client.event
        async def on_ready():
            logging.debug("DiscordBot is ready.")
            guilds = self.client.guilds
            # Начальный опрос для всех гильдий
            for g in guilds:
                logging.debug(f"Initial poll for guild_id={g.id}.")
                await self.initial_poll(g.id)
            self.initialized = True

        @self.client.event
        async def on_voice_state_update(member, before, after):
            if not self.initialized:
                return
            guild = member.guild
            logging.debug(f"Voice state update in guild_id={guild.id} for member={member.name}.")
            user_id_list, max_in_channel, total_in_channels = await self.get_current_users_in_channels(guild.id)

            # Проверяем всех пользователей, отслеживающих этот сервер
            for user_str in self.storage.get_all_users():
                user_settings = self.storage.get_user_settings(user_str)
                if not user_settings:
                    continue
                servers = user_settings.get("servers", [])
                if guild.id not in servers:
                    continue
                mode = user_settings.get("mode", "total")
                threshold = user_settings.get("threshold", 0)

                # Подсчет по режиму
                if mode == "total":
                    count = total_in_channels
                    user_list = user_id_list
                    channel_name = f"Сервер {guild.name} (все каналы)"
                else:
                    # mode = max_channel
                    # max_in_channel уже рассчитан
                    # Чтобы найти конкретные пользователи макс. канала,
                    # сделаем еще раз проход (оптимизация не критична)
                    max_count = 0
                    max_channel_users = []
                    max_channel_name = ""
                    for vc in guild.voice_channels:
                        members_list = [m for m in vc.members if not m.bot]
                        c_len = len(members_list)
                        if c_len > max_count:
                            max_count = c_len
                            max_channel_users = [m.name for m in members_list]
                            max_channel_name = vc.name
                    count = max_count
                    user_list = max_channel_users
                    channel_name = f"Сервер {guild.name}, канал {max_channel_name}"

                old_count = self.tracked_data.get((user_str, guild.id), 0)
                if old_count < threshold and count >= threshold:
                    logging.debug(f"Threshold reached for user_id={user_str} on guild_id={guild.id}.")
                    if self.telegram_bot:
                        self.telegram_bot.notify_user(user_str, channel_name, count, user_list)
                self.tracked_data[(user_str, guild.id)] = count

    def set_telegram_bot(self, telegram_bot):
        logging.debug("Setting telegram bot in DiscordBot.")
        self.telegram_bot = telegram_bot

    async def start_async(self):
        logging.debug("Starting DiscordBot client.")
        await self.client.start(DISCORD_BOT_TOKEN)

    def check_server_permissions(self, server_id):
        logging.debug(f"Checking permissions on server_id={server_id}.")
        guild = self.client.get_guild(server_id)
        if not guild:
            return False
        me = guild.me
        if not me:
            return False
        return True

    async def track_voice_channels(self):
        logging.debug("Tracking voice channels for all guilds.")
        for guild in self.client.guilds:
            await self.initial_poll(guild.id)

    async def get_current_users_in_channels(self, server_id):
        logging.debug(f"Getting current users in channels for server_id={server_id}.")
        guild = self.client.get_guild(server_id)
        if not guild:
            return [], 0, 0
        user_set = set()
        max_count = 0
        total_count = 0
        for vc in guild.voice_channels:
            members_list = [m for m in vc.members if not m.bot]
            c_len = len(members_list)
            total_count += c_len
            if c_len > max_count:
                max_count = c_len
            for m in members_list:
                user_set.add(m.name)
        return list(user_set), max_count, total_count

    async def initial_poll(self, server_id):
        logging.debug(f"Initial poll for server_id={server_id}.")
        user_id_list, max_in_channel, total_in_channels = await self.get_current_users_in_channels(server_id)
        # Инициализируем tracked_data для всех пользователей, отслеживающих этот сервер
        for user_str in self.storage.get_all_users():
            user_settings = self.storage.get_user_settings(user_str)
            if not user_settings:
                continue
            servers = user_settings.get("servers", [])
            if server_id not in servers:
                continue
            self.tracked_data[(user_str, server_id)] = 0
