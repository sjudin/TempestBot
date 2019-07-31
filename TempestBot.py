import discord
import time
import asyncio
import datetime

from SheetReader import get_not_set_raiders
from discord.ext import commands
from TOKEN import TOKEN

class TempestBot(object):
    def __init__(self):
        self.CHANNEL_ID = 605728010661789698
        # self.CHANNEL_ID = 527183820382797824 Raid disc
        self.bot = commands.Bot(command_prefix=".")

        # Wait until bot is started
        print("test")

    async def wait_until_ready(self):
        print("waiting until ready")
        await self.bot.wait_until_ready()
        print("done waiting")

        self.channel = self.bot.get_channel(self.CHANNEL_ID)
        await self.channel.send('TempestBot is alive!')
        self.not_set_raiders = get_not_set_raiders()

    # Sends a message notifying all raiders that have not set attendance
    async def send_attendance_message(self):
        self.not_set_raiders = get_not_set_raiders()

        members = list()

        # If a members displayname matches one of the names in not_set_raiders (from spreadsheet)
        # we add it to the members list (this raider has not set attendence)
        for member in self.channel.guild.members:
            for raider in self.not_set_raiders:
                if raider in member.display_name:
                    members.append(member)

        # If everyone has signed attendance we dont need to notify
        if not members:
            return

        await channel.send('Currently missing signups from these people for this reset:')
        await channel.send(', '.join([ r.mention for r in members]))
        

    async def send_attendance_message_task():
        while True:
            weekday = datetime.datetime.now().weekday()
            # Remind on mondays, tuesdays and wednesdays
            if weekday in [0, 1, 2]:
                await self.send_attendance_message()
                await asyncio.sleep(43200)


Bot = TempestBot()
Bot.spin()


class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await client.wait_until_ready()


