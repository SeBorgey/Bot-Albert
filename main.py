import asyncio
import os
import discord
import logging
from dotenv import load_dotenv
from discord.ext import commands


class TutorialBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Greetings
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} ({self.bot.user.id})')

    # Reconnect
    @commands.Cog.listener()
    async def on_resumed(self):
        print('Bot has reconnected!')

    # Error Handlers
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Uncomment line 26 for printing debug
        # await ctx.send(error)

        # Unknown command
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('Invalid Command!')

        # Bot does not have permission
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('Bot Permission Missing!')


async def load_extensions(bot):
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
            except Exception as e:
                print(f"Failed to load extension {filename}: {e}")


async def main():
    # Gateway intents
    intents = discord.Intents.default()
    intents.message_content = True  # Enable message content intent
    intents.members = True
    intents.presences = True

    # Bot prefix
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),
                       description='A Simple Tutorial Bot', intents=intents)

    # Logging
    logger = logging.getLogger('discord')
    # logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # Load extension
    await load_extensions(bot)

    # Add cog
    await bot.add_cog(TutorialBot(bot))

    # Loading data from .env file
    load_dotenv()
    token = os.getenv('TOKEN')

    # Run bot
    await bot.start(token, reconnect=True)


if __name__ == '__main__':
    asyncio.run(main())