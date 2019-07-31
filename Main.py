import discord
from discord.ext import commands
from TOKEN import TOKEN
import time
from SheetReader import get_not_set_raiders
import asyncio
import datetime

client = commands.Bot(command_prefix=".")
# CHANNEL_ID = 527183820382797824 # Tempest raid-discussion
CHANNEL_ID = 605728010661789698 # Testing channel


@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)

    channel = client.get_channel(CHANNEL_ID)
    await channel.send('TempestBot is now alive!')

@client.event
async def on_message(message):
    await client.wait_until_ready()

    channel = client.get_channel(CHANNEL_ID)

    if message.author == client.user:
        return

    if message.content == '.Ping':
        await channel.send('Yes I am alive!')

    if message.content != '.Attendance':
        return

    not_set_raiders = get_not_set_raiders()
    print(not_set_raiders)
    if not not_set_raiders:
        await channel.send('All raiders are signed for this week, good job!')
        return

    await send_attendance_message(not_set_raiders)

async def attendance_msg_task():
    not_set_raiders = get_not_set_raiders()
    while True:
        weekday = datetime.datetime.now().weekday()
        # Remind on mondays, tuesdays and wednesdays
        if weekday in [0, 1, 2]:
            await asyncio.sleep(43200)
            await send_attendance_message(not_set_raiders)
            continue


async def send_attendance_message(not_set_raiders):
    await client.wait_until_ready()
    members = list()
    channel = client.get_channel(CHANNEL_ID)

    for member in channel.guild.members:
        for raider in not_set_raiders:
            if raider in member.display_name:
                members.append(member)
            
    if not members:
        return

    await channel.send('Currently missing signups from these people for this reset:')
    await channel.send(', '.join([ r.mention for r in members]))
    await channel.send('https://tenor.com/view/shame-go-t-game-of-thrones-walk-of-shame-shameful-gif-4949558')



client.loop.create_task(attendance_msg_task())
client.run(TOKEN)
