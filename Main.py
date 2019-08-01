import discord
from discord.ext import commands
from TOKEN import TOKEN
import time
from SheetReader import get_not_set_raiders
import asyncio
import datetime
import subprocess

client = commands.Bot(command_prefix=".")
CHANNEL_ID = 527183820382797824 # Tempest raid-discussion
# CHANNEL_ID = 605728010661789698 # Testing channel


@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)
    await client.get_user(496028306232049694).send('TempestBot has started')

@client.event
async def on_message(message):
    await client.wait_until_ready()

    channel = client.get_channel(CHANNEL_ID)

    if message.author == client.user:
        return

    if message.author.id == 496028306232049694:
        if message.content == '.Ping':
            await message.author.send('Yes I am alive!')
            await message.author.send('Currently running on server {0}'.format(channel.guild))
            return

        if message.content == '.Log':
            proc = subprocess.check_output(['sudo', 'systemctl', 'status', 'TempestBot.service'])
            await message.author.send('stdout:\n{0}\n----------\n----------'.format(proc.decode('utf-8')))


    if message.content != '.Attendance':
        return

    not_set_raiders = get_not_set_raiders()
    print(not_set_raiders)
    if not not_set_raiders:
        await channel.send('All raiders are signed for this week, good job!')
        return

    await send_attendance_message(not_set_raiders)

async def attendance_msg_task():
    await client.wait_until_ready()

    while not client.is_closed:
        weekday = datetime.datetime.now().weekday()
        # Remind on mondays, tuesdays and wednesdays
        if weekday in [0, 1, 2]:
            await asyncio.sleep(43200)
            not_set_raiders = get_not_set_raiders()
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



client.loop.create_task(attendance_msg_task())
client.run(TOKEN)
