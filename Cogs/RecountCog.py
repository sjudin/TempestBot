import discord
import collections
import operator
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import subprocess

from discord.ext import tasks, commands
from Cogs.slpp import slpp as lua

trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

color_dict = {
            'Druid': (1.0, 0.49, 0.04, 1),
            'Hunter': (0.67, 0.83, 0.45, 1),
            'Mage': (0.25, 0.78, 0.92, 1),
            'Paladin': (0.96, 0.55, 0.73, 1),
            'Priest': (1.00, 1.00, 1.00, 1),
            'Rogue': (1.00, 0.96, 0.41, 1),
            'Shaman': (0.00, 0.44, 0.87, 1),
            'Warlock': (0.53, 0.53, 0.93, 1),
            'Warrior': (0.78, 0.61, 0.43, 1)
            }

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
        log_length = 8

        f = open('E:\\WoW\\WTF\\Account\\SJUDIN\\Netherwing\\Loriell\\SavedVariables\\Recount.lua').read()
        # subprocess.call(['cp', '/home/pi/projects/ShareFile/Recount.lua', '/home/pi/projects/TempestBot/'])
        # f = open('/home/pi/projects/TempestBot/Recount.lua').read()

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

        total_healing = 0

        for _, player in recount_data['combatants'].items():
            if(player['isFriend'] and player['isPlayer'] == 1):
                unsorted_healers[_] = {}
                unsorted_healers[_]['Class'] = player['class']
                unsorted_healers[_]['HealingDone'] = player['Fights']['LastFightData']['Healing']
                total_healing = total_healing + player['Fights']['LastFightData']['Healing']


        healers = collections.OrderedDict(sorted(unsorted_healers.items(), key=lambda x: x[1]['HealingDone'], reverse = True))

        names = list()
        values = list()
        classes = list()

        for key, value in healers.items():
            names.append(key)
            values.append(value['HealingDone'])
            classes.append(value['Class'])

        names = names[:log_length]
        values = values[:log_length]
        classes = classes[:log_length]

        names.reverse()
        values.reverse()
        classes.reverse()

        healers['Duration'] = recount_data['combatants']['Loriell']['Fights']['LastFightData']['ActiveTime']

        names_pos = [0, 0.8, 1.6, 2.4, 3.2, 4, 4.8, 5.6]

        fig, ax = plt.subplots()
        barlist = ax.barh(names_pos,values)
        ax.set_facecolor('dimgrey')
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        for i, v in enumerate(values):
            hps = v/healers['Duration']
            percent = 100*v/total_healing
            print(hps, percent)

            name_text = ax.text(0, i - i*0.2, '  {}'.format(names[i]), color='white',
                    weight='heavy', va='center')
            healing_text = ax.text(values[-1], i - i*0.2, '{0} ({1:0.1f} , {2:0.1f}%)'.format(int(v), hps, percent),
                    color='white', ha='right', va='center', weight='heavy')

            name_text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'),
                                        path_effects.Normal()])
            healing_text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'),
                                        path_effects.Normal()])

        for index, bar in enumerate(barlist):
            bar.set_color(color_dict.get(classes[index], 'r'))
            bar.set_edgecolor('black')
         
        plt.ylim(-0.4, names_pos[-1]+.4)

        plt.ioff()
        plt.savefig('log.png')

        # await message.edit(content = healers)
        await ctx.send(file=discord.File('log.png'))


def setup(client):
    client.add_cog(Recount(client))
