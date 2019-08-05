import discord
import datetime
import subprocess
import asyncio
import aioschedule as schedule
import time

from discord.ext import tasks, commands
from Helptexts import Helptexts
from SheetReader import get_not_set_raiders
from Main import CHANNEL_ID
from datetime import datetime

trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

help = Helptexts()

# Admin commands
def check_if_trusted_ids(ctx):
    return ctx.author.id in trusted_ids

class Attendance(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Initialize jobs
        for day in self.client.notification_days:
            for time in self.client.notification_times:
                s = self.days_dict(day, time)
                if s is not None:
                    s.do(self.attendance_msg_task)

    async def attendance_msg_task(self):
        not_set_raiders, sheet_title = get_not_set_raiders()
        await self.send_attendance_message(ctx=None, not_set_raiders=not_set_raiders, sheet_title=sheet_title)

    @commands.command(name='Jobs', help='Returns current jobs from aioschedule')
    @commands.check(check_if_trusted_ids)
    async def jobs_command(self, ctx):
        embed = discord.Embed(title='Jobs')
        [embed.add_field(name='Job', value=job) for job in self.client.scheduler.jobs]
        await ctx.send(embed=embed)
    
    @commands.command(name='Ping', help=help.Ping)
    @commands.check(check_if_trusted_ids)
    async def ping_command(self, ctx):
        if ctx.author.id in self.client.trusted_ids:
            await ctx.send('Currently running on server {0}'.format(self.client.channel.guild))
            await ctx.send('Bot is currently set to ping at times {}. Type .changeTimes to change this'.format(', '.join(self.client.notification_times)))
            await ctx.send('Bot is currently set to ping at days {}. Type .changeDays to change this'.format(', '.join([str(a) for a in self.client.notification_days])))
            await ctx.send('Output from current not set raiders: {0}'.format(get_not_set_raiders()))

    @commands.command(name='changeTimes', help=help.changeTimes)
    @commands.check(check_if_trusted_ids)
    async def change_times_command(self, ctx, *args):
        import time
        try:
            for arg in args:
                val = time.strptime(arg, '%H:%M')
        except(ValueError) as e:
            await ctx.send('Input was not correct, should be a list of times on the format HH:MM in range 00:00 - 23:59 separated by spaces\nExample: 09:00 18:00 21:00\nnote that 24:00 should be 00:00')
            return
        # All times are valid, set new times
        self.client.notification_times = [datetime.strptime(arg, '%H:%M').strftime('%H:%M') for arg in args]
        self.client.scheduler.clear()

        for day in self.client.notification_days:
            for time in self.client.notification_times:
                s = self.days_dict(day, time)
                if s is not None:
                    s.do(self.attendance_msg_task)
        await ctx.send('Notification times were changed. New times are: {}'.format(', '.join(self.client.notification_times)))

    @commands.command(name='changeDays', help=help.changeDays)
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
        # Reschedule tasks to new times
        self.client.scheduler.clear()
        for day in self.client.notification_days:
            for time in self.client.notification_times:
                s = self.days_dict(day, time)
                if s is not None:
                    s.do(self.attendance_msg_task)

        await ctx.send('Notification days were changed. New days are: {}'.format(', '.join([str(a) for a in self.client.notification_days])))


    @commands.command(name='Log', help=help.Log)
    @commands.check(check_if_trusted_ids)
    async def log_command(self, ctx):
        if ctx.author.id in self.client.trusted_ids:
            proc = subprocess.check_output(['sudo', 'systemctl', 'status', 'TempestBot.service'])
            await ctx.send('stdout:\n{0}\n----------\n----------'.format(proc.decode('utf-8')))

    @commands.command(name='Repo', help='Link to repository for this bot')
    async def repo_command(self, ctx):
        await ctx.send('https://github.com/sjudin/TempestBot')


    @commands.command(name='Attendance', help=help.Attendance)
    @commands.check(check_if_trusted_ids)
    async def attendance_command(self, ctx):
        not_set_raiders, sheet_title = get_not_set_raiders()
        if not not_set_raiders:
            await ctx.send('All raiders are signed for this reset, good job!')
            return

        await self.send_attendance_message(ctx, not_set_raiders, sheet_title)


    async def send_attendance_message(self, ctx, not_set_raiders, sheet_title):
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

            await self.client.channel.send('Currently missing {} from these people:'.format(sheet_title))
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

            await ctx.send('Currently missing {} from these people:'.format(sheet_title))
            await ctx.send(', '.join([ r.mention for r in members]))

        except(AttributeError) as e:
            await self.client.channel.send('Currently missing {} from these people:'.format(sheet_title))
            await self.client.channel.send('Could not find a guild, printing output from not_set_raiders: {}'.format(not_set_raiders))

    def days_dict(self, day, time):
        # function that add new jobs to scheduler
        # given a day (int: 0-6) and a time (string: 00:00-23:59)
        days = {
                0: self.client.scheduler.every().monday.at(time),
                1: self.client.scheduler.every().tuesday.at(time),
                2: self.client.scheduler.every().wednesday.at(time),
                3: self.client.scheduler.every().thursday.at(time),
                4: self.client.scheduler.every().friday.at(time),
                5: self.client.scheduler.every().saturday.at(time),
                6: self.client.scheduler.every().sunday.at(time),
                }
        try:
            return days[day]
        except(KeyError) as e:
            return None

def setup(client):
    client.add_cog(Attendance(client))


