import discord
import sqlite3
import random
from discord.ext import commands
from discord import Embed


def db_connect():
    return sqlite3.connect(r'C:\Users\Nathan\Documents\CS321\database.sqlite3')


bot = commands.Bot(command_prefix='$')

connection = db_connect()
cursor = connection.cursor()
userData = """
CREATE TABLE funusers (
    userid integer PRIMARY KEY,
    coins integer NOT NULL)"""
#cursor.execute(userData)
funuser_sql = "INSERT INTO funusers (userid, coins) VALUES (?, ?)"
update_sql = "UPDATE funusers SET coins = ? where userid = ?"
client = commands.Bot(command_prefix=".")


# helper function to get users balance of coins
def getbalance(ctx):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    return result[0]


# wait until ready before doing commands
@client.event
async def on_ready():
    print("bot is ready!")


# for errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass all required arguements. Type .help to get a list of commands and their usage.")


# pong
@client.command(brief='pong', description='tells you your ping')
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)}ms')


# first message sent sets user in database
@client.event
async def on_message(message):
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format(message.author.id))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(funuser_sql, (message.author.id, 0,))
    await client.process_commands(message)


# shutdowns down bot.
# IMPORTANT
# need to use it to save any coin updates
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    connection.commit()
    await ctx.bot.logout()


# daily coins
@client.command()
async def daily(ctx):
    result = getbalance(ctx)
    cursor.execute(update_sql, (result + 200, ctx.message.author.id))
    result = getbalance(ctx)
    embed = Embed(title="Current coin total is:", description="{}".format(result))
    await ctx.send(embed=embed)


# get your current balance
@client.command(aliases=['bal'])
async def balance(ctx):
    result = getbalance(ctx)
    embed = Embed(title="Current coin total is:", description="{}".format(result))
    await ctx.send(embed=embed)


# flip a coin 50/50, gets double if win
@client.command()
async def coin(ctx, money: int, side):
    result = getbalance(ctx)
    if result < money:
        embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
        await ctx.send(embed=embed)
        return
    embed = Embed(title="You are betting {} coins on {}".format(money, side))
    rnum = random.randint(1, 2)
    if (side == "h" or side == "heads") and rnum == 1:
        cursor.execute(update_sql, (result + money * 2, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Success!", value="It was heads! You earned {} coins.".format(money * 2))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)
    elif (side == "t" or side == "tails") and rnum == 2:
        cursor.execute(update_sql, (result + money * 2, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Success!", value="It was tails! You earned {} coins.".format(money * 2))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)
    elif (side == "t" or side == "tails") and rnum == 1:
        cursor.execute(update_sql, (result - money, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Failure!", value="It was heads! You lost {} coins.".format(money))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)
    else:
        cursor.execute(update_sql, (result - money, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Failure!", value="It was tails! You lost {} coins.".format(money))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)


# role a 5 or a 6 to triple money
@client.command()
async def dice(ctx, money: int):
    result = getbalance(ctx)
    if result < money:
        embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
        await ctx.send(embed=embed)
        return
    embed = Embed(title="You are betting {} coins on a roll of 5 or 6".format(money))
    rnum = random.randint(1, 6)
    if rnum < 5:
        cursor.execute(update_sql, (result - money, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Failure!", value="You rolled a {}! You lost {} coins.".format(rnum, money))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)
    else:
        cursor.execute(update_sql, (result + money * 3, ctx.message.author.id))
        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        result = cursor.fetchone()
        embed.add_field(name="Success!", value="You rolled a {}! You won {} coins.".format(rnum, money * 3))
        embed.add_field(name="New Balance:", value="{}".format(result[0]), inline=False)
        await ctx.send(embed=embed)


# for debugging purposes, lets you set your coins
@client.command()
@commands.has_permissions(administrator=True)
async def setbal(ctx, money: int):
    cursor.execute(update_sql, (money, ctx.message.author.id))
    result = getbalance(ctx)
    await ctx.send("Current bal is now: {} coins.".format(result))


client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')
