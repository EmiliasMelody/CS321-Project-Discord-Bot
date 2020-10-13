import discord
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$daily'):
        recieve_daily()

client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')

def recieve_daily():
    