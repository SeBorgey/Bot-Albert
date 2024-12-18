import json
import time
import logging
from discord.ext import commands
import telebot

# Initialize the Telegram bot
bot = telebot.TeleBot('6832477390:AAE-DnGXPYO5DEUVLcS_EfQHk1hBY6EWGBk')

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceMemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('./databases/voice_member_count.json', 'w') as file:
            file.write("{\n}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        member_id = str(member.id)
        try:
            with open('./databases/voice_member_count.json', 'r') as file:
                voice_member_data = json.load(file)
                new_voice_member_channel = str(member.voice.channel.id)
                new_voice_member_id = str(member.id)
                number_of_users = 0
                delta = 0
                for item in list(voice_member_data.values()):
                    number_of_users = max(len(item), number_of_users)

                for item in list(voice_member_data.values()):
                    if new_voice_member_id in item:
                        item.remove(new_voice_member_id)
                        delta -= 1
                # Update existing voice data
                if new_voice_member_channel in voice_member_data:
                    voice_member_data[new_voice_member_channel] += [new_voice_member_id]
                    delta += 1
                    with open('./databases/voice_member_count.json', 'w') as update_voice_member_data:
                        json.dump(voice_member_data, update_voice_member_data, indent=4)

                        time.sleep(1)

                # Add new voice data
                else:
                    voice_member_data[new_voice_member_channel] = [new_voice_member_id]
                    delta += 1
                    with open('./databases/voice_member_count.json', 'w') as new_voice_member_data:
                        json.dump(voice_member_data, new_voice_member_data, indent=4)
                        time.sleep(1)
                amount = 3
                if number_of_users >= amount:
                    pass
                else:
                    number_of_users += delta
                    if number_of_users >= amount:
                        text = "В дсе собралось " + str(number_of_users) + " человека"
                        bot.send_message("189590002", text)

        except AttributeError:
            # Remove voice data
            for remove_keys, remove_values in voice_member_data.items():
                if member_id in remove_values:
                    remove_values.remove(member_id)

            with open('./databases/voice_member_count.json', 'w') as remove_voice_member_data:
                json.dump(voice_member_data, remove_voice_member_data, indent=4)

async def setup(bot):
    await bot.add_cog(VoiceMemberCount(bot))