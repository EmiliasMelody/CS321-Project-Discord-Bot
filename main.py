import discord
import sqlite3
import random
from discord.ext import commands
from discord import Embed
import csv
import random


def db_connect():
    return sqlite3.connect(r'/Users/nikita/Documents/GitHub/CS321-Project-Discord-Bot\database.sqlite3')


bot = commands.Bot(command_prefix='$')

connection = db_connect()
cursor = connection.cursor()
userData = """
CREATE TABLE funusers (
    userid integer PRIMARY KEY,
    coins integer NOT NULL,
    username text NOT NULL)"""
# cursor.execute(userData)

funuser_sql = "INSERT INTO funusers (userid,coins, username) VALUES (?, ?,?)"
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
        cursor.execute(funuser_sql, (message.author.id, 0, message.author.name,))
    await client.process_commands(message)


# shutdowns down bot.
# IMPORTANT
# need to use it to save any coin updates
@client.command()
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    connection.commit()
    await ctx.bot.logout()


# daily coins
@client.command()
async def daily(ctx):
    result = getbalance(ctx)
    table = "funusers"
    field = "coins"
    id = ctx.message.author.id
    money = result + 200
    cursor.execute(("UPDATE %s SET %s = %s WHERE %s ") % (table, field, money, id))
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
    table = "funusers"
    field = "coins"
    user_id = ctx.message.author.id
    cursor.execute("UPDATE %s SET %s = %s WHERE %s" % (table, field, money, user_id))
    result = getbalance(ctx)
    embed = Embed(title="Current bal is now: {} coins.".format(result))
    await ctx.send(embed=embed)


@client.command(aliases=['sendmoney'])
async def sendMoney(ctx, arg, message_user):
    amount = int(arg)
    # gets the user's tag
    tag = message_user
    # checks if its an actual tag
    if tag.find("!") != -1:
        tagNumber = tag[3:len(tag) - 1]
    else:
        tagNumber = -99

    result = getbalance(ctx)
    newmoney = result - int(arg)
    if (newmoney < 0):
        # checks if you have enough money to send
        embed = Embed(title="Cannot send money: Insufficient funds")
        await ctx.send(embed=embed)
    elif (newmoney >= 0):
        # checks if the user is valid
        money = int(arg)
        table = "funusers"
        field = "coins"

        # checks to see if the name exits
        cursor.execute("SELECT * FROM funusers")
        rows = cursor.fetchall()
        found = 0
        print("tag")
        print(tagNumber)
        for row in rows:
            print(row)
            if (row[0] == int(tagNumber)):
                found = row
        if found == 0 or tagNumber == -99:
            embed = Embed(title="Cannot send money: Not a valid user")
            await ctx.send(embed=embed)

        # if the user does exist
        else:
            # updates the recievers account)
            rec_money = found[1] + amount
            cursor.execute(("UPDATE %s SET %s = %d WHERE %s") % (table, field, rec_money, tagNumber))

            # updates the senders account
            send_id = ctx.message.author.id
            send_money = getbalance(ctx) - amount
            cursor.execute("UPDATE %s SET %s = %s WHERE %s" % (table, field, send_money, send_id))
            result = getbalance(ctx)
            embed = Embed(title="Current coin total is:", description="{}".format(result))
            embed2 = Embed(title="Money sent!")
            await ctx.send(embed=embed)
            await ctx.send(embed=embed2)


@client.command(aliases=['unscramble'])
async def unscrambleGame(ctx):
    embed = Embed(title="Starting unscramble game: \n Remember to put a .guess in front of your guess!")
    originalWord = getWord()
    scrammbledWord = scrammble(originalWord)
    embed.add_field(name="UNSCRAMBLE: ", value="{}".format(scrammbledWord), inline=False)
    await ctx.send(embed=embed)

    x = {'value': 3}

    @client.command(aliases=['guess'])
    async def unscrambleGuess(ctx, arg):
        totalguess = x['value']
        if arg == originalWord:
            embed2 = Embed(title="Good job you got the right word \n You won a 100 coins! ")
            await ctx.send(embed=embed2)
            result = getbalance(ctx)
            table = "funusers"
            field = "coins"
            id = ctx.message.author.id
            money = result + 100
            cursor.execute(("UPDATE %s SET %s = %s WHERE %s ") % (table, field, money, id))
            result = getbalance(ctx)
        if arg != originalWord and totalguess != 0:
            x['value'] -= 1
            totalguess = x['value']
            embed3 = Embed(title="Wrong guess! Try again! \n Only {} chances left".format(totalguess))
            await ctx.send(embed=embed3)
        if totalguess == 0:
            embed4 = Embed(title="All out of guesses! Good luck next time!")
            await ctx.send(embed=embed4)


# used in the unscramble game gets a random word
def getWord():
    # gets a random word

    # picks a random line number to start at
    index = random.randint(0, 4343)
    counter = 0
    word = ""
    # opens a csv file of a bunch of words
    with open('words.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if index == counter:
                # if the counter matches the random number gets the word
                word = row['word']
                # if the word is too small recalls the function
                if len(word) < 3:
                    getWord()
                break
            else:
                # increments the counter
                counter += 1
    print(word)
    return word


# used in unscramble game - scrambles the word
def scrammble(word):
    # scrambles the word
    l = list(word)
    random.shuffle(l)
    newWord = ''.join(l)
    print(newWord)
    return newWord


client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')
