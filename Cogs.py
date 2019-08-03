import discord
import datetime
import subprocess
import asyncio
import time

from discord.ext import tasks, commands
from SheetReader import get_not_set_raiders
from Main import CHANNEL_ID
from datetime import datetime

trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

# Checks that Attendance command can only be called from raid-discussion or from users with trusted_ids
def check_if_dm_or_channel(ctx):
    return ctx.channel == CHANNEL_ID or ctx.author.id in trusted_ids

# Admin commands
def check_if_trusted_ids(ctx):
    return ctx.author.id in trusted_ids

class Attendance(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.attendance_msg_task.start()

    @commands.command(name='Ping', help='Pings bot to see if it is alive, it will return some info about its current status')
    @commands.check(check_if_trusted_ids)
    async def ping_command(self, ctx):
        if ctx.author.id in self.client.trusted_ids:
            await ctx.send('Currently running on server {0}'.format(self.client.channel.guild))
            await ctx.send('Bot is currently set to ping at times {}. Type .changeTimes to change this'.format(', '.join(self.client.notification_times)))
            await ctx.send('Bot is currently set to ping at days {}. Type .changeDays to change this'.format(', '.join([str(a) for a in self.client.notification_days])))
            await ctx.send('Output from current not set raiders: {0}'.format(get_not_set_raiders()))

    @commands.command(name='changeTimes', help='Changes the current times when notifications should be sent. \
                    Times should be on HH:MM format and separated by spaces. Example usage:\n.changeTimes 09:00 12:00 15:00')
    @commands.check(check_if_trusted_ids)
    async def change_times_command(self, ctx, *args):
        try:
            for arg in args:
                val = time.strptime(arg, '%H:%M')
        except(ValueError):
            await ctx.send('Input was not correct, should be a list of times on the format HH:MM separated by spaces\nExample: 09:00 18:00 21:00')
            return
        # All times are valid, set new times
        self.client.notification_times = [datetime.strptime(arg, '%H:%M').strftime('%H:%M') for arg in args]
        await ctx.send('Notification times were changed. New times are: {}'.format(', '.join(self.client.notification_times)))

    @commands.command(name='changeDays', help='Changes the current days when notifications should be sent. \
                    dates should be integers from 0-6 that represent the days of the week. Example usage:\n.changeDays 1 2 3\n\nThis will notify on tue/wed/thur')
    @commands.check(check_if_trusted_ids)
    async def change_days_command(self, ctx, *args):
        new_notification_days = list()

        try:
            for a in args:
                    if int(a) < 0 or int(a) > 6:
                        raise ValueError

                    new_notification_days.append(int(a))

        except(ValueError):
            await ctx.send('Input was not correct, should be numbers between 0-6 that represent days of the week separated by spaces\nExample: 0 1 2\nCorresponds to Mon-tue-wed')
            return

        self.client.notification_days = new_notification_days
        await ctx.send('Notification days were changed. New days are: {}'.format(', '.join([str(a) for a in self.client.notification_days])))


    @commands.command(name='Log', help='Sends log information from systemctl service on Raspberry. Mostly used by Loriell for logging purposes.')
    @commands.check(check_if_trusted_ids)
    async def log_command(self, ctx):
        if ctx.author.id in self.client.trusted_ids:
            proc = subprocess.check_output(['sudo', 'systemctl', 'status', 'TempestBot.service'])
            await ctx.send('stdout:\n{0}\n----------\n----------'.format(proc.decode('utf-8')))


    @commands.command(name='Attendance', help='Lists attendance from all raiders. This command can be called by anyone but must be from the #raid-discussion channel.\n\
                                               Officers can DM this command to the bot and it will show up in #raid-discussion aswell.')
    @commands.check(check_if_dm_or_channel)
    async def attendance_command(self, ctx):
        not_set_raiders = get_not_set_raiders()
        if not not_set_raiders:
            await ctx.send('All raiders are signed for this reset, good job!')
            return

        await self.send_attendance_message(ctx, not_set_raiders)


    async def send_attendance_message(self, ctx, not_set_raiders):
        await self.client.wait_until_ready()
        members = list()

        # If called from task
        if not ctx:
            for member in self.client.channel.guild.members:
                for raider in not_set_raiders:
                    if raider in member.display_name:
                        members.append(member)

            if not not_set_raiders:
                return

            await self.client.channel.send('Currently missing signups from these people for this reset:')
            try:
                await self.client.channel.send(', '.join([ r.mention for r in members]))
            except(discord.HTTPException):
                await self.client.channel.send('Error occured')
                await self.client.channel.send(not_set_raiders)
            return

        # If called from command
        try:
            for member in ctx.guild.members:
                for raider in not_set_raiders:
                    if raider in member.display_name:
                        members.append(member)

            if not not_set_raiders:
                await self.client.channel.send('All raiders have signed up for this reset, good job!')
                return

            await ctx.send('Currently missing signups from these people for this reset:')
            await ctx.send(', '.join([ r.mention for r in members]))

        except(AttributeError) as e:
            await self.client.channel.send('Currently missing signups from these people for this reset:')
            await self.client.channel.send('Could not find a guild, printing output from not_set_raiders: {}'.format(not_set_raiders))


    @tasks.loop(minutes=1.0)
    async def attendance_msg_task(self):
        weekday = datetime.now().weekday()
        now = datetime.strftime(datetime.now(), '%H:%M')
        # Remind on mondays, tuesdays and wednesdays
        if weekday in self.client.notification_days and now in self.client.notification_times:
            not_set_raiders = get_not_set_raiders()
            await self.send_attendance_message(ctx=None, not_set_raiders=not_set_raiders)

    @attendance_msg_task.before_loop
    async def wait_for_bot(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Attendance(client))
