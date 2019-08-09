import discord
from discord.ext import tasks, commands
import glob
import os

trusted_ids = [496028306232049694, 180084840950005760, 137153880839553024, 136459243359436800, 219492968564785154, 442729218342780957]

def check_if_trusted_ids(ctx):
    return ctx.author.id in trusted_ids

class Assignments(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='Assignment', aliases=['a'], help='Assignment for different bossfights. To see list of all fights give command without argument. To see assignments for FLK, input commnad .a FLK')
    @commands.check(check_if_trusted_ids)
    async def assignment_command(self, ctx, *args):
        # base_path = 'E:\\python_projects\\TempestBot\\assignments'
        # l = glob.glob(base_path + '\\*.txt')
        base_path = '/home/pi/projects/TempestBot/assignments'
        l = glob.glob(base_path + '/*.txt')

        if not args:
            embed = discord.Embed(title='Assignments')
            [embed.add_field(name='Fight', value=os.path.basename(fight)) for fight in l]
            await ctx.send(embed=embed)
            return

        for arg in args:
            path = base_path + '/' + arg + '.txt'
            if os.path.exists(path):
                file = open(path, 'r')
                await ctx.send(file.read())
            else:
                await ctx.send('Assignment file {} does not exist'.format(path))

def setup(client):
    client.add_cog(Assignments(client))
