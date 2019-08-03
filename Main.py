import discord
from discord.ext import commands
from TOKEN import TOKEN
from SheetReader import get_not_set_raiders
import datetime
import asyncio
import subprocess
from datetime import datetime


class TempestBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.CHANNEL_ID = 527183820382797824 # Tempest raid-discussion
        self.CHANNEL_ID = 605728010661789698 # Testing channel

        self.channel = None
        self.admin_user = None

        self.notification_times = ['09:00','15:00','21:00']
        self.notification_days = [0, 1, 2]


#client = commands.Bot(command_prefix='.', case_insensitivte=True)
client = TempestBot(command_prefix='.', case_insensitive=True)
CHANNEL_ID = client.CHANNEL_ID

cogs = ['Cogs']

@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)

    for cog in cogs:
        client.load_extension(cog)

    # Set this after client is ready because of threading issues
    client.channel = client.get_channel(client.CHANNEL_ID)
    client.admin_user = client.get_user(496028306232049694)

    await client.get_user(496028306232049694).send('TempestBot has started')


if __name__ == '__main__':
#    client.loop.create_task(attendance_msg_task())
    client.run(TOKEN)
