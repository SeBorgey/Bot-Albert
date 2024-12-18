import asyncio
import discord
from config import DISCORD_BOT_TOKEN

class DiscordBot:
    def __init__(self, storage):
        self.storage = storage
        self.telegram_bot = None
        self.client = discord.Client(intents=discord.Intents(guilds=True, voice_states=True, members=True))
        self.initialized = False
        self.tracked_data = {}

        @self.client.event
        async def on_ready():
            guilds = self.client.guilds
            for g in guilds:
                await self.initial_poll(g.id)
            self.initialized = True

        @self.client.event
        async def on_voice_state_update(member, before, after):
            if not self.initialized:
                return
            guild = member.guild
            user_id_list, max_in_channel, total_in_channels = await self.get_current_users_in_channels(guild.id)
            for user_str in self.storage.get_all_users():
                user_settings = self.storage.get_user_settings(user_str)
                if not user_settings or user_settings.get("server_id") != guild.id:
                    continue
                mode = user_settings.get("mode", "total")
                threshold = user_settings.get("threshold", 0)
                channels = user_settings.get("channels", [])
                if len(channels) == 0:
                    continue
                if mode == "total":
                    count = total_in_channels
                    user_list = user_id_list
                    channel_name = "All tracked"
                else:
                    max_count = 0
                    max_channel_users = []
                    max_channel_name = ""
                    for ch_id in channels:
                        ch = guild.get_channel(ch_id)
                        if ch and ch.members:
                            c_len = len([m for m in ch.members if not m.bot])
                            if c_len > max_count:
                                max_count = c_len
                                max_channel_users = [m.name for m in ch.members if not m.bot]
                                max_channel_name = ch.name
                    count = max_count
                    user_list = max_channel_users
                    channel_name = max_channel_name
                old_count = self.tracked_data.get((user_str, guild.id), 0)
                if old_count < threshold and count >= threshold:
                    if self.telegram_bot:
                        self.telegram_bot.notify_user(user_str, channel_name, count, user_list)
                self.tracked_data[(user_str, guild.id)] = count

    def set_telegram_bot(self, telegram_bot):
        self.telegram_bot = telegram_bot

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.client.start(DISCORD_BOT_TOKEN))
        loop.run_forever()

    def check_server_permissions(self, server_id):
        guild = self.client.get_guild(server_id)
        if not guild:
            return False
        me = guild.me
        if not me:
            return False
        return True

    async def track_voice_channels(self):
        for guild in self.client.guilds:
            await self.initial_poll(guild.id)

    async def get_current_users_in_channels(self, server_id):
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
        user_id_list, max_in_channel, total_in_channels = await self.get_current_users_in_channels(server_id)
        for user_str in self.storage.get_all_users():
            user_settings = self.storage.get_user_settings(user_str)
            if not user_settings or user_settings.get("server_id") != server_id:
                continue
            self.tracked_data[(user_str, server_id)] = 0
