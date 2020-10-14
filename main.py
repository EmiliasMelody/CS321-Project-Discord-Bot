import discord
import sqlite3
from discord.ext import commands

def db_connect():
    return sqlite3.connect(r'C:\Users\Connor\PycharmProjects\pythonProject\database.sqlite3')

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

def tester(uniqid):
    print(uniqid)
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format(uniqid))
    result = cursor.fetchone()
    print("this is your id: {}".format(result))

@client.event
async def on_ready():
    print("bot is ready!")

@client.command()
async def ping(ctx):
    await ctx.send(f'Ping is {round(client.latency * 1000)}ms')
@client.event
async def on_message(message):
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format(message.author.id))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(funuser_sql, (message.author.id, 0,))
    await client.process_commands(message)
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    connection.commit()
    await ctx.bot.logout()

@client.command()
async def daily(ctx):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    cursor.execute(update_sql, (result[0] + 200, ctx.message.author.id))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    await ctx.send("your current total is: {}".format(result[0]))
client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')

