import discord
import collections
import operator
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib as mpl
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

        # f = open('E:\\WoW\\WTF\\Account\\SJUDIN\\Netherwing\\Loriell\\SavedVariables\\Recount.lua').read()
        subprocess.call(['cp', '/home/pi/mounts/SavedVariables/Recount.lua', '/home/pi/projects/TempestBot/'])
        f = open('/home/pi/projects/TempestBot/Recount.lua').read()

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
            if 'Fights' not in player or 'LastFightData' not in player['Fights']:
                continue
            if(player['isFriend'] and player['isPlayer'] == 1):
                unsorted_healers[_] = {}
                unsorted_healers[_]['Class'] = player['class']
                # unsorted_healers[_]['HealingDone'] = player['Fights']['LastFightData']['Healing']
                unsorted_healers[_]['HealingDone'] = player['Fights']['LastFightData'].get('Healing', 0)
                unsorted_healers[_]['Overhealing'] = 0
                
                if 'OverHeals' in player['Fights']['LastFightData']:
                    for spell, value in player['Fights']['LastFightData']['OverHeals'].items():
                        unsorted_healers[_]['Overhealing'] += value['amount']

                # total_healing = total_healing + player['Fights']['LastFightData']['Healing']
                total_healing = total_healing + unsorted_healers[_]['HealingDone']



        healers = collections.OrderedDict(sorted(unsorted_healers.items(), key=lambda x: x[1]['HealingDone'], reverse = True))

        names = list()
        values = list()
        classes = list()
        overhealing = list()

        for key, value in healers.items():
            names.append(key)
            values.append(value['HealingDone'])
            classes.append(value['Class'])
            overhealing.append(value['Overhealing'])

        names = names[:log_length]
        values = values[:log_length]
        classes = classes[:log_length]
        overhealing = overhealing[:log_length]

        names.reverse()
        values.reverse()
        classes.reverse()
        overhealing.reverse()

        healers['Duration'] = recount_data['combatants']['Loriell']['Fights']['LastFightData']['ActiveTime']

        names_pos = [0, 0.8, 1.6, 2.4, 3.2, 4, 4.8, 5.6]

        # fig, ax = plt.subplots()
        fig = plt.figure(figsize=(8,6))
        ax = plt.subplot(111)

        for side in ['top', 'bottom', 'left', 'right']:
            ax.spines[side].set_visible(False)

        barlist_overhealing = ax.barh(names_pos,overhealing, left=values, color='dimgrey')
        barlist_healing = ax.barh(names_pos,values)

        ax.set_facecolor('grey')

        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        mpl.rcParams['savefig.pad_inches'] = 0


        for i, v in enumerate(values):
            hps = v/healers['Duration']
            percent = 100*v/total_healing
            oh = int(overhealing[i])

            name_text = ax.text(0, i - i*0.2, '  {}'.format(names[i]), color='white',
                    weight='heavy', va='center')
            healing_text = ax.text(max(overhealing) + values[-1], i - i*0.2, '{0:,} ({1:0.1f} , {2:0.1f}%)    OH: {3:,} {4:0.1f}%'.format(int(v), hps, percent, oh, 100*oh/(int(v)+oh)),
                    color='white', ha='right', va='center', weight='heavy')

            name_text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'),
                                        path_effects.Normal()])
            healing_text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'),
                                        path_effects.Normal()])

        for index, bar in enumerate(barlist_healing):
            bar.set_color(color_dict.get(classes[index], 'r'))
            bar.set_edgecolor('black')

        for index, bar in enumerate(barlist_overhealing):
            bar.set_edgecolor('black')
         
        plt.ylim(-0.4, names_pos[-1]+.4)

        plt.ioff()
        plt.savefig('log.png', bbox_inches='tight', pad_inches=0)

        await message.edit(content = recount_data['FoughtWho'][0])
        await ctx.send(file=discord.File('log.png'))


def setup(client):
    client.add_cog(Recount(client))
