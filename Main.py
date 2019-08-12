import discord
import datetime
import asyncio
import subprocess
import aioschedule as schedule

from datetime import datetime
from discord.ext import commands
from TOKEN import TOKEN
from SheetReader import get_not_set_raiders

class TempestBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.CHANNEL_ID = 527183820382797824 # Tempest raid-discussion
        self.CHANNEL_ID = 605728010661789698 # Testing channel

        self.channel = None
        self.admin_user = None

        self.scheduler = schedule.default_scheduler

        self.notification_times = ['09:00','15:00','21:00']
        self.notification_days = [0, 1, 2]

        # Loriell, Ryndaris, Demia, Sugi, Vanaroth, Klashgora
        self.trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

    async def timer(self):
        # Timer function that runs pending jobs in scheduler,
        # Is meant to be run in clients event loop by calling 
        # client.loop.create_task(self.timer())
        while True:
            await self.scheduler.run_pending()
            await asyncio.sleep(1)


client = TempestBot(command_prefix='.', case_insensitive=True)
CHANNEL_ID = client.CHANNEL_ID
cogs = ['Cogs.AttendanceCog', 'Cogs.AssignmentsCog', 'Cogs.RecountCog']

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
    client.loop.create_task(client.timer())
    client.run(TOKEN)
