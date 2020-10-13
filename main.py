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
client = discord.Client()

def tester(uniqid):
    print(uniqid)
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format(uniqid))
    result = cursor.fetchone()
    print("this is your id: {}".format(result))
def recieve_daily(authorid):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(authorid))
    result = cursor.fetchone()
    cursor.execute(funuser_sql, (authorid, result[0] + 200))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(authorid))
    result = cursor.fetchone()
    return result

@client.event
async def on_message(message):
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format(message.author.id))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(funuser_sql, (message.author.id, 0,))
    if message.author == client.user:
        return
    if message.content.startswith("hello"):
        await message.channel.send("hello!!!")
    if message.content.startswith("$daily"):
        dail = recieve_daily(message.author.id)
        await message.channel.send(dail)
@commands.cooldown(1, 86400, commands.BucketType.user)
@bot.command()
async def daily(ctx):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    cursor.execute(funuser_sql, (ctx.message.author.id, result + 200,))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    await ctx.message.channel.send("Your current total is: {}".format(result))
client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')

