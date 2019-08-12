import discord
import collections
import operator
import matplotlib.pyplot as plt

from discord.ext import tasks, commands
from Cogs.slpp import slpp as lua

trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

def check_if_trusted_ids(ctx):
    return ctx.author.id in trusted_ids

class Recount(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='Recount', aliases=['r'])
    @commands.check(check_if_trusted_ids)
    async def recount_command(self, ctx, *args):
        message = await ctx.send('Processing recount data...')

        a = lua.SLPP()

        f = open('E:\\WoW\\WTF\\Account\\SJUDIN\\Netherwing\\Loriell\\SavedVariables\\Recount.lua').read()
        # f = open('/home/pi/projects/ShareFile/recount.lua').read()

        f = '{' + f.split('{', 1)[-1]
        recount_data = a.decode(f)

        if not args:
            embed = discord.Embed(title='Last fights')
            l = ['{}\n'.format(r) for r in recount_data['FoughtWho']]
            [embed.add_field(name=index+1, value=value, inline=False) for index, value in enumerate(recount_data['FoughtWho'])]
            await message.edit(embed=embed)
            return

        healers = collections.OrderedDict()
        unsorted_healers = dict()

        for _, player in recount_data['combatants'].items():
            if(player['isFriend'] and player['isPlayer'] == 1):
                unsorted_healers[_] = {}
                unsorted_healers[_]['Class'] = player['class']
                unsorted_healers[_]['HealingDone'] = player['Fights']['LastFightData']['Healing']


        healers = collections.OrderedDict(sorted(unsorted_healers.items(), key=lambda x: x[1]['HealingDone'], reverse = True))
        # healers['Duration'] = recount_data['combatants']['Loriell']['Fights']['LastFightData']['ActiveTime']
        names = list()
        values = list()

        for key, value in healers.items():
            names.append(key)
            values.append(value['HealingDone'])

        names = names[:6]
        values = values[:6]
        names.reverse()
        values.reverse()
        plt.barh(names, values)
        plt.ioff()
        plt.savefig('log.png')
        

        # await message.edit(content = healers)
        await ctx.send(file=discord.File('log.png'))


def setup(client):
    client.add_cog(Recount(client))
