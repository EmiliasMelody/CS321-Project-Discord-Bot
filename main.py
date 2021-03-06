import asyncio

import discord
from discord.utils import get
import sqlite3
from discord.ext import commands
from discord import Embed
import csv
import random

items = {'Balloon': (80, "Throw a water balloon at your friends", "Buy with .shop balloon"),
         'Valueable Member role': (
         10000, "Show off how much money you have with this vanity role", "Buy with .shop vm"),
         'VIP role': (50000, "Show off even more!", "Buy with .shop vip"),
         'Mystery Box': (
         100, "A mystery box that contains a random amount of coins or maybe other items", "Buy with .shop mb"),
         'Daily Multiplier (1.5x)': (1000, "Multiplies your daily coins by 1.5", "Buy with .shop daily"),
         'Daily Multiplier (2.0x)': (
         2000, "Multiplies your daily coins by 2. Must have previous multiplier", "Buy with .shop daily"),
         'Daily Multiplier (3.0x)': (
         5000, "Multiplies your daily coins by 3. Must have previous multiplier", "Buy with .shop daily"),
         'Global Multiplier (1.5x)': (1500, "Multiplies all coins you earn by 1.5", "Buy with .shop global"),
         'Global Multiplier (2.0x)': (
         3000, "Multiplies all coins you earn by 2. Must have previous multiplier", "Buy with .shop global"),
         'Global Multiplier (3.0x)': (
         6000, "Multiplies all coins you earn by 3. Must have previous multiplier", "Buy with .shop global")}


def db_connect():
    return sqlite3.connect(r'C:\Users\Nathan\Documents\CS321\database.sqlite3')


bot = commands.Bot(command_prefix='$')

connection = db_connect()
cursor = connection.cursor()
userData = """
CREATE TABLE funusers (
    userid integer PRIMARY KEY,
    coins integer NOT NULL,
	balloons INTEGER,
	vm INTEGER,
	vip INTEGER,
	daily REAL,
	global REAL)"""
#cursor.execute(userData)
funuser_sql = "INSERT INTO funusers (userid, coins, balloons, vm, vip, daily, global) VALUES (?, ?, ?, ?, ?, ?, ?)"
update_sql = "UPDATE funusers SET coins = ? where userid = ?"
client = commands.Bot(command_prefix=".")


class Card:
    def __init__(self, suit, value, ace):
        self.suit = suit
        self.value = value
        self.ace = ace


class Deck:
    def __init__(self, num=0):
        self.cards = []
        if num == 0:
            self.makeDeck()
        elif num == 1:
            self.makeBlack()

    def makeDeck(self):
        for i in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for v in range(1, 14):
                if v == 1:
                    self.cards.append(Card(i, v, True))
                else:
                    self.cards.append(Card(i, v, False))

    def makeBlack(self):
        for i in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for v in range(1, 11):
                if v == 1:
                    self.cards.append(Card(i, v, True))
                else:
                    self.cards.append(Card(i, v, False))

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            rnum = random.randint(0, i)
            self.cards[i], self.cards[rnum] = self.cards[rnum], self.cards[i]

    def draw(self):
        return self.cards.pop()


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, deck):
        return self.hand.append(deck.draw())

    def total(self):
        tot = 0
        for i in self.hand:
            tot += i.value
        return tot

    def lastCard(self):
        return self.hand[-1]

    def topCard(self):
        return self.hand[0]

    def showHand(self):
        x = 1
        for i in self.hand:
            print(f"card {x} is {i.value} of {i.suit}")
            x += 1
        return

    def dropCard(self):
        return self.hand.pop()

    def numcardsinHand(self):
        x = 1
        for i in self.hand:
            x += 1
        return x

    def addCards(self, pile):
        for card in pile:
            self.hand.append(card)


# helper function to get users balance of coins
def getbalance(ctx):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    return result[0]

#helper to get the global coin modifier of a user
def globalMod(id):
    cursor.execute("SELECT global FROM funusers WHERE userid = {}".format(id))
    result = cursor.fetchone()
    return result[0]

#only used for instances in which the global coin multiplier is used
#we use id here instead of ctx because we have multiplayer games and ctx would only provide player 1
def giveCoins(id, baseValue):
	result = globalMod(id)
	coins = baseValue * result
	cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(id))
	temp = cursor.fetchone()
	result = temp[0]
	cursor.execute(update_sql, (result + coins, id))
	return coins


# used in the unscramble game gets a random word
def getWord(minLength):
    # gets a random word

    # picks a random line number to start at
    index = random.randint(0, 4341)
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
                if len(word) < minLength:
                    getWord(1)
                break
            else:
                # increments the counter
                counter += 1
    #print(word)
    return word


# used in unscramble game - scrambles the word
def scrammble(word):
    # scrambles the word
    l = list(word)
    random.shuffle(l)
    newWord = ''.join(l)
    print(newWord)
    return newWord


# wait until ready before doing commands
@client.event
async def on_ready():
    print("bot is ready!")


# for errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass all required arguements. Type .help to get a list of commands and their usage.")

    if isinstance(error, asyncio.TimeoutError):
        await ctx.send("Command Timeout.")


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
        cursor.execute(funuser_sql, (message.author.id, 0, 0, 0, 0, 1.0, 1.0))
    await client.process_commands(message)


# shutdowns down bot.
# IMPORTANT
# need to use it to save any coin updates
@client.command(brief="Shuts down the Bot.", description="A safe way to manually shut down the bot. ONLY AVAILABLE TO THE SERVER OWNER.")
@commands.is_owner()
#swap this out with the previous line for debugging if not the server owner
#@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    connection.commit()
    await ctx.bot.logout()


#helper to get the daily coin modifier of a user
def dailyMod(ctx):
    cursor.execute("SELECT daily FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    return result[0]


# daily coins
@commands.cooldown(1, 86400, commands.BucketType.user)
@client.command(brief="Gives you your daily coins.", description="Can be used once per day to give you 200 coins.")
async def daily(ctx):
	mod = dailyMod(ctx)
	result = getbalance(ctx)
	coins = 200 * mod
	cursor.execute(update_sql, (result + coins, ctx.message.author.id))
	result = getbalance(ctx)
	embed = Embed(title="Current coin total is:", description="{}".format(result))
	await ctx.send(embed=embed)


# get your current balance
@client.command(aliases=['bal'], brief="Tells you how many coins you have.", description="Tells you how many coins you have. Can also be called using .bal")
async def balance(ctx):
    result = getbalance(ctx)
    embed = Embed(title="Current coin total is:", description="{}".format(result))
    await ctx.send(embed=embed)


# flip a coin 50/50, gets double if win
@client.command(brief="Flip a coin, win coins.", description="Flip a coin. If you guess which side it lands on right, you double your bet!\n\n<money> -- How much you want to bet\n<side> -- Which side you think it will land on. Can format as 'heads' and 'tails' or 'h' and 't'.")
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
@client.command(brief="Roll the dice, win coins.", description="Bet however much you want. On a roll of a 5 or a 6, you double your wager!\n\n<money> -- How much you want to bet.")
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
@client.command(brief="FOR TESTING PURPOSES ONLY", description="Lets you set how many coins you have. Must be an admin on the server.")
@commands.has_permissions(administrator=True)
async def setbal(ctx, money: int):
    cursor.execute(update_sql, (money, ctx.message.author.id))
    result = getbalance(ctx)
    await ctx.send("Current bal is now: {} coins.".format(result))


@client.command(aliases=['sendmoney'], brief="Send money to your friends!", description="Allows you to send coins to another user.\n\n<arg> -- how much to send\n<message_user> -- the person you are sending money to")
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
    if newmoney < 0:
        # checks if you have enough money to send
        embed = Embed(title="Cannot send money: Insufficient funds")
        await ctx.send(embed=embed)
    elif newmoney >= 0:
        # checks if the user is valid
        money = int(arg)
        table = "funusers"
        field = "coins"

        # checks to see if the name exits
        cursor.execute("SELECT * FROM funusers")
        rows = cursor.fetchall()
        found = 0
        for row in rows:
            if row[0] == int(tagNumber):
                found = row
        if found == 0 or tagNumber == -99:
            embed = Embed(title="Cannot send money: Not a valid user")
            await ctx.send(embed=embed)

        # if the user does exist
        else:
            # updates the recievers account)
            rec_money = found[1] + amount
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(rec_money, found[0]))

            # updates the senders account
            send_id = ctx.message.author.id
            send_money = getbalance(ctx) - amount
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(newmoney, send_id))
            result = getbalance(ctx)
            embed = Embed(title="Current coin total is:", description="{}".format(result))
            embed2 = Embed(title="Money sent!")
            await ctx.send(embed=embed)
            await ctx.send(embed=embed2)


@client.command(brief="Go head to head with someone in this classic card game.", description="Play against the bot or another user. On each round, players flip a card from their deck. The player with the higher card wins that round. To play against the bot, put nothing in the [message_user] field.\n\n<money> -- how much you want to bet on the game\n<message_user> -- put someone's name here if you want to play with them")
async def war(ctx, money, message_user=None):
    deck = Deck(0)
    deck.shuffle()
    if message_user is None:
        result = getbalance(ctx)
        if result < money:
            await ctx.send("Not enough coins in your bank! Sorry!")
            return
        embedt = Embed(title=f"Game of War, you are betting {money}",
                       description="Use .flip to flip a card, and .q to quit."
                                   "only the person who started the game needs to use .flip")
        await ctx.send(embed=embedt)
        playerwins = []
        npcwins = []
        playerone = Player(ctx.message.author.id)
        npc = Player("Bot")
        while deck.cards[0] is not None:
            playerone.draw(deck)
            npc.draw(deck)
        msg = await client.wait_for('message', timeout=120.0,
                                    check=lambda message: message.author == ctx.author \
                                                          and message.channel == ctx.channel)
        victor = 0
        while ".q" != msg.content:
            if ".flip" == msg.content:

                # next two statements deal with if the player/bot's hand is empty
                if playerone.topCard() is None:
                    # this means player one still has cards in bank
                    if playerwins[0] is not None:
                        while playerwins[0] is not None:
                            playerone.hand.append(playerwins.pop())
                    # this means that playerone lost
                    else:
                        victor = 2
                        break
                if npc.topCard() is None:
                    # this means player one still has cards in bank
                    if npcwins[0] is not None:
                        while npcwins[0] is not None:
                            npc.hand.append(npcwins.pop())
                    # this means that playerone lost
                    else:
                        victor = 1
                        break

                # deals with actual game play
                playercard = playerone.topCard()
                npccard = npc.topCard()
                if playercard.value < npccard.value:
                    npcwins.append(npc.hand.pop(0))
                    npcwins.append(playerone.hand.pop(0))
                    gameembed = Embed(title="War!", description="The bot won this round!")
                    gameembed.add_field(name="Player's Card:", value=f"{playercard.value} of {playercard.suit}")
                    gameembed.add_field(name="Bot's Card:", value=f"{npccard.value} of {npccard.suit}")
                    await ctx.send(embed=gameembed)
                elif playercard.value > npccard.value:
                    playerwins.append(npc.hand.pop(0))
                    playerwins.append(playerone.hand.pop(0))
                    gameembed = Embed(title="War!", description="The player won this round!")
                    gameembed.add_field(name="Player's Card:", value=f"{playercard.value} of {playercard.suit}")
                    gameembed.add_field(name="Bot's Card:", value=f"{npccard.value} of {npccard.suit}")
                    await ctx.send(embed=gameembed)
                # for ties, will keep flipping one card until no more tie.
                else:
                    gameembed = Embed(title="War!", description="There was a tie!")
                    gameembed.add_field(name="Player's Card:", value=f"{playercard.value} of {playercard.suit}")
                    gameembed.add_field(name="Bot's Card:", value=f"{npccard.value} of {npccard.suit}")
                    qui = True
                    count = 0
                    while qui is True:
                        count += 1
                        playercard = playerone.hand[count]
                        npccard = npc.hand[count]
                        if playercard.value < npccard.value:
                            i = 0
                            while i <= count:
                                npcwins.append(npc.hand.pop(0))
                                npcwins.append(playerone.hand.pop(0))
                            gameembed = Embed(title="War!", description="The bot won this round!"
                                                                        " All cards go to it!")
                            gameembed.add_field(name="Player's Card:", value=f"{playercard.value} of {playercard.suit}")
                            gameembed.add_field(name="Bot's Card:", value=f"{npccard.value} of {npccard.suit}")
                            await ctx.send(embed=gameembed)
                            qui = False
                        elif playercard.value > npccard.value:
                            i = 0
                            while i <= count:
                                npcwins.append(npc.hand.pop(0))
                                npcwins.append(playerone.hand.pop(0))
                            playerwins.append(npc.hand.pop(0))
                            playerwins.append(playerone.hand.pop(0))
                            gameembed = Embed(title="War!", description="The player won this round!"
                                                                        " All cards go to them")
                            gameembed.add_field(name="Player's Card:", value=f"{playercard.value} of {playercard.suit}")
                            gameembed.add_field(name="Bot's Card:", value=f"{npccard.value} of {npccard.suit}")
                            await ctx.send(embed=gameembed)
                            qui = False

        # now the finish message for when the game is over
        if victor == 1:
            res = getbalance(ctx)
            embedfinish = Embed(title="Game over!", description="The player has won!")
            cursor.execute(update_sql, (res + money, ctx.message.author.id))
            cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
            res = cursor.fetchone()
            embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
            await ctx.send(embed=embedfinish)
        elif victor == 2:
            res = getbalance(ctx)
            embedfinish = Embed(title="Game over!", description="The bot has won!")
            cursor.execute(update_sql, (res - money, ctx.message.author.id))
            cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
            res = cursor.fetchone()
            embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
            await ctx.send(embed=embedfinish)

    ###################################################################################################################
    # below is all code for if there is a second player, not a bot. #
    # Almost identical except slight changes to how money is taken for both accounts. #
    ###################################################################################################################
    else:
        result = getbalance(ctx)
        if result < money:
            await ctx.send("Not enough coins in Player 1's bank! Sorry!")
            return
        if message_user.find("!") != -1:
            tagNumber = message_user[3:len(message_user) - 1]
        else:
            tagNumber = -99
        # checks to see if the name exits
        cursor.execute("SELECT * FROM funusers")
        rows = cursor.fetchall()
        found = 0
        for row in rows:
            if row[0] == int(tagNumber):
                found = row
        if found == 0 or tagNumber == -99:
            embed = Embed(title="Cannot Start Game: Not a valid user")
            await ctx.send(embed=embed)

        cursor.execute(f"SELECT coins FROM funusers WHERE userid = {tagNumber}")
        res = cursor.fetchone()
        if res[0] < money:
            await ctx.send("Not enough coins in Player 2's bank! Sorry!")
            return
        # start the actual game
        else:
            embedt = Embed(title=f"Game of War, you are betting {money}",
                           description="Use .flip to flip a card, and .q to quit."
                                       "only the person who started the game needs to use .flip")
            await ctx.send(embed=embedt)
            playerwins = []
            npcwins = []
            playerone = Player(ctx.message.author.id)
            npc = Player(tagNumber)
            while deck.cards[0] is not None:
                playerone.draw(deck)
                npc.draw(deck)
            msg = await client.wait_for('message', timeout=120.0,
                                        check=lambda message: message.author == ctx.author \
                                                              and message.channel == ctx.channel)
            victor = 0
            while ".q" != msg.content:
                if ".flip" == msg.content:

                    # next two statements deal with if the player/bot's hand is empty
                    if playerone.topCard() is None:
                        # this means player one still has cards in bank
                        if playerwins[0] is not None:
                            while playerwins[0] is not None:
                                playerone.hand.append(playerwins.pop())
                        # this means that playerone lost
                        else:
                            victor = 2
                            break
                    if npc.topCard() is None:
                        # this means player one still has cards in bank
                        if npcwins[0] is not None:
                            while npcwins[0] is not None:
                                npc.hand.append(npcwins.pop())
                        # this means that playerone lost
                        else:
                            victor = 1
                            break

                    # deals with actual game play
                    playercard = playerone.topCard()
                    npccard = npc.topCard()
                    if playercard.value < npccard.value:
                        npcwins.append(npc.hand.pop(0))
                        npcwins.append(playerone.hand.pop(0))
                        gameembed = Embed(title="War!", description="Player 2 has won this round!")
                        gameembed.add_field(name="Player 1's Card:", value=f"{playercard.value} of {playercard.suit}")
                        gameembed.add_field(name="Player 2's Card:", value=f"{npccard.value} of {npccard.suit}")
                        await ctx.send(embed=gameembed)
                    elif playercard.value > npccard.value:
                        playerwins.append(npc.hand.pop(0))
                        playerwins.append(playerone.hand.pop(0))
                        gameembed = Embed(title="War!", description="Player 1 has won this round!")
                        gameembed.add_field(name="Player 1's Card:", value=f"{playercard.value} of {playercard.suit}")
                        gameembed.add_field(name="Player 2's Card:", value=f"{npccard.value} of {npccard.suit}")
                        await ctx.send(embed=gameembed)
                    # for ties, will keep flipping one card until no more tie.
                    else:
                        gameembed = Embed(title="War!", description="There was a tie!")
                        gameembed.add_field(name="Player 1's Card:", value=f"{playercard.value} of {playercard.suit}")
                        gameembed.add_field(name="Player 2's Card:", value=f"{npccard.value} of {npccard.suit}")
                        qui = True
                        count = 0
                        while qui is True:
                            count += 1
                            playercard = playerone.hand[count]
                            npccard = npc.hand[count]
                            if playercard.value < npccard.value:
                                i = 0
                                while i <= count:
                                    npcwins.append(npc.hand.pop(0))
                                    npcwins.append(playerone.hand.pop(0))
                                gameembed = Embed(title="War!", description="Player 2 has won this round!"
                                                                            " All cards go to them!")
                                gameembed.add_field(name="Player 1's Card:",
                                                    value=f"{playercard.value} of {playercard.suit}")
                                gameembed.add_field(name="Player 2's Card:", value=f"{npccard.value} of {npccard.suit}")
                                await ctx.send(embed=gameembed)
                                qui = False
                            elif playercard.value > npccard.value:
                                i = 0
                                while i <= count:
                                    npcwins.append(npc.hand.pop(0))
                                    npcwins.append(playerone.hand.pop(0))
                                playerwins.append(npc.hand.pop(0))
                                playerwins.append(playerone.hand.pop(0))
                                gameembed = Embed(title="War!", description="Player 1 has won this round!"
                                                                            " All cards go to them")
                                gameembed.add_field(name="Player 1's Card:",
                                                    value=f"{playercard.value} of {playercard.suit}")
                                gameembed.add_field(name="Player 2's Card:",
                                                    value=f"{npccard.value} of {npccard.suit}")
                                await ctx.send(embed=gameembed)
                                qui = False

            # now the finish message for when the game is over
            if victor == 1:
                res = getbalance(ctx)
                rec_money = found[1] - money
                embedfinish = Embed(title="Game over!", description="Player 1 has won!")
                cursor.execute(update_sql, (res + money, ctx.message.author.id))
                cursor.execute(f"UPDATE funusers SET coins = {rec_money} WHERE {tagNumber}")
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance Player 1:", value="{}".format(res[0]), inline=False)
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(tagNumber))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance Player 2:", value="{}".format(res[0]), inline=False)
                await ctx.send(embed=embedfinish)
            elif victor == 2:
                res = getbalance(ctx)
                rec_money = found[1] + money
                embedfinish = Embed(title="Game over!", description="Player 2 has won!")
                cursor.execute(update_sql, (res - money, ctx.message.author.id))
                cursor.execute(f"UPDATE funusers SET coins = {rec_money} WHERE {tagNumber}")
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance Player 1:", value="{}".format(res[0]), inline=False)
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(tagNumber))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance Player 2:", value="{}".format(res[0]), inline=False)
                await ctx.send(embed=embedfinish)


@client.command(aliases=['black'], brief="Blackjack", description="Get as close to 21 as possible without going over.\n\n<money> -- how much you want to bet")
async def blackjack(ctx, money: int):
    result = getbalance(ctx)
    if result < money:
        ctx.send("Not enough coins in your bank! Sorry!")
        return

    embed = Embed(title="Starting Blackjack, you are betting {}!".format(money),
                  description="Use .black hit to get another card, .black stay to pass.")
    await ctx.send(embed=embed)
    deck = Deck(1)
    deck.shuffle()
    user = Player(ctx.message.author.id)
    pc = Player("Bot")
    user.draw(deck)
    user.draw(deck)
    pc.draw(deck)
    pc.draw(deck)
    embedplayer = Embed(title="Your current hand is:")
    embedplayer.add_field(name="Card 1:", value="{} of {}".format(user.hand[0].value, user.hand[0].suit, inline=False))
    embedplayer.add_field(name="Card 2:", value="{} of {}".format(user.hand[1].value, user.hand[1].suit, inline=False))
    embedplayer.add_field(name="Total:", value=f"{user.total()}")

    await ctx.send(embed=embedplayer)
    q = 0
    while q == 0:
        if pc.total() <= 14:
            pc.draw(deck)
            if pc.lastCard() == 1:
                pc.draw(deck)
        else:
            q = 1
    embedbot = Embed(title="Bots cards are:")
    embedbot.add_field(name="Card 1:", value="Hidden")
    q = 1
    total = 0
    for c in pc.hand:
        if q != 1:
            embedbot.add_field(name="Card {}:".format(q), value=f"{c.value} of {c.suit}")
            total += c.value
            q += 1
        else:
            q += 1
    embedbot.add_field(name=f"Bot's Total Revealed cards:", value=f"{total}")
    await ctx.send(embed=embedbot)
    msg = await client.wait_for('message', timeout=120.0,
                                check=lambda message: message.author == ctx.author \
                                                      and message.channel == ctx.channel)
    print(msg)
    while ".q" != msg.content:
        if ".hit" == msg.content:
            user.draw(deck)
            embedplayer.remove_field(len(user.hand) + 1)
            embedplayer.add_field(name=f"Card {len(user.hand)}",
                                  value=f"{user.lastCard().value} of {user.lastCard().suit}")
            embedplayer.add_field(name="Total:", value=f"{user.total()}")
            await ctx.send(embed=embedplayer)
            await ctx.send(embed=embedbot)
            if user.total() > 21:

                res = getbalance(ctx)
                embedfinish = Embed(title="Game Finished. Results:")
                embedfinish.add_field(name="Bot total:", value=f"{pc.total()}")
                embedfinish.add_field(name="Player total:", value=f"{user.total()}")
                if user.total() > 21 and pc.total() > 21:
                    embedfinish.add_field(name="Nobody won!", value="try again next time")
                elif user.total() > 21 or pc.total() > user.total():

                    embedfinish.add_field(name="Bot won!", value="try again next time")
                    cursor.execute(update_sql, (res - money, ctx.message.author.id))
                    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                    res = cursor.fetchone()
                    embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
                elif pc.total() > 21 or user.total() > pc.total():
                    embedfinish.add_field(name="Player won!", value="Great job!")
                    cursor.execute(update_sql, (res + money, ctx.message.author.id))
                    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                    res = cursor.fetchone()
                    embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
                else:
                    embedfinish.add_field(name="There was a tie!", value="Nobody wins!")
                await ctx.send(embed=embedfinish)

            msg.content = ".q"
        elif ".stay" == msg.content:
            res = getbalance(ctx)
            embedfinish = Embed(title="Game Finished. Results:")
            embedfinish.add_field(name="Bot total:", value=f"{pc.total()}")
            embedfinish.add_field(name="Player total:", value=f"{user.total()}")
            if user.total() > 21 and pc.total() > 21:
                embedfinish.add_field(name="Nobody won!", value="try again next time")
            elif user.total() > 21 or pc.total() > user.total():

                embedfinish.add_field(name="Bot won!", value="try again next time")
                cursor.execute(update_sql, (res - money, ctx.message.author.id))
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
            elif pc.total() > 21 or user.total() > pc.total():
                embedfinish.add_field(name="Player won!", value="Great job!")
                cursor.execute(update_sql, (res + money, ctx.message.author.id))
                cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
                res = cursor.fetchone()
                embedfinish.add_field(name="New Balance:", value="{}".format(res[0]), inline=False)
            else:
                embedfinish.add_field(name="There was a tie!", value="Nobody wins!")
            await ctx.send(embed=embedfinish)
            msg.content = ".q"
        msg = await client.wait_for('message', timeout=120.0,
                                    check=lambda message: message.author == ctx.author \
                                                          and message.channel == ctx.channel)


@client.command(aliases=['unscramble'], brief="Try to unscramble the given word.", description="You get 3 tries to guess the word. To make a guess, simply type '.guess' followed by your guess (e.g. if you wanted to guess the word 'example', you would type '.guess example'). Costs 20 coins to play. You can earn 100 coins for guessing correctly.")
async def unscrambleGame(ctx):
    embed = Embed(title="Starting unscramble game")
    # checks if enough coins
    result = getbalance(ctx)
    if result < 20:
        embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
        await ctx.send(embed=embed)
        return
    temp = cursor.fetchone()
    cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(result - 20, ctx.message.author.id))
    result = getbalance(ctx)

    unscrambleGame.originalWord = getWord(1)
    scrammbledWord = scrammble(unscrambleGame.originalWord)
    await ctx.send(embed=embed)
    embed1 = Embed(title="Remember to put a .guess in front of your guess!")
    embed2 = Embed(title="UNSCRAMBLE: " + scrammbledWord)
    await ctx.send(embed=embed1)
    await ctx.send(embed=embed2)

    x = {'value': 3}

    @client.command(aliases=['guess'])
    async def unscrambleGuess(ctx, arg):
        totalguess = x['value']
        if arg == unscrambleGame.originalWord:
            coins = giveCoins(ctx.message.author.id, 100)
            embed1 = Embed(title="Good job you got the right word")
            embed2 = Embed(title="You won a {} coins!".format(coins))
            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
            result = getbalance(ctx)
            embedm = Embed(title="Current coin total is:", description="{}".format(result))
            await ctx.send(embed=embedm)
            x['value'] = 3
            totalguess = 3
            return

        if arg != unscrambleGame.originalWord and totalguess != 0:
            embed3 = Embed(title="Wrong guess! Try again ")
            await ctx.send(embed=embed3)
            x['value'] -= 1
            totalguess = x['value']
            embed4 = Embed(title="Only {} chances left".format(totalguess))
            await ctx.send(embed=embed4)

        if totalguess == 0:
            x['value'] = 3
            totalguess = 3
            embed5 = Embed(title="All out of guesses! Good luck next time! \n The word was {}". format(unscrambleGame.originalWord))
            await ctx.send(embed=embed5)
            return
    return


@client.command(brief="The classic game of hangman.", description="Guess letters one at a time until all of the word is revealed. You get up to 6 incorrect guesses. Costs 20 coins to play and you get 100 coins if you win. After the game begins, you can just type the letter you want to guess.")
async def hangman(ctx):
    # checks if the user has enough coins
    result = getbalance(ctx)
    if result < 20:
        embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
        await ctx.send(embed=embed)
        return
    cursor.execute(update_sql, (result - 20, ctx.message.author.id))

    done = 0
    guesses = ""
    wrongGuesses = 0
    correctGuesses = 0
    word = getWord(6)
    word.lower()
    blanks = ""
    for x in range(len(word)):
        blanks += "#"
    # used later to fill in the blanks
    blanksList = list(blanks)

    start = hangmanPrint("Game start!", wrongGuesses, blanks, guesses)
    await ctx.send(embed=start)

    while done == 0:

        def check(m):
            if (len(m.content) > 1):
                return False
            else:
                return True

        response = await client.wait_for('message', check=check)

        msg = "" + response.content

        if len(msg) > 1:
            embed = Embed(title="Please only guess one letter at a time")
            await ctx.send(embed=embed)
            continue

        if msg in guesses:
            embed = Embed(title="You already guessed that one...")
            await ctx.send(embed=embed)
            continue

        guesses += msg
        oldBlanks = blanks

        for x in range(len(word)):
            if (word[x]) == msg:
                correctGuesses += 1
                blanksList[x] = msg
        blanks = "".join(blanksList)

        if wrongGuesses >= 5:
            done = -1
            embed = Embed(title="All out of guesses. Better luck next time!")
            await ctx.send(embed=embed)
            break

        if oldBlanks == blanks:
            wrongGuesses += 1
            embed = hangmanPrint("Incorrect Guess", wrongGuesses, blanks, guesses)
            await ctx.send(embed=embed)
            continue

        if correctGuesses >= len(word):
            done = 1
            coins = giveCoins(ctx.message.author.id, 100)
            embed = hangmanPrint("Congrats, you won and earned {} coins!".format(coins), wrongGuesses, blanks, guesses)
            await ctx.send(embed=embed)
            break
        else:
            embed = hangmanPrint("Correct! Keep guessing...", wrongGuesses, blanks, guesses)
            await ctx.send(embed=embed)
            continue


def hangmanPrint(message, wrongGuesses, blanks, guesses):
    chances = (
        "() () () () () ()", "(x) () () () () ()", "(x) (x) () () () ()", "(x) (x) (x) () () ()",
        "(x) (x) (x) (x) () ()",
        "(x) (x) (x) (x) (x) ()", "(x) (x) (x) (x) (x) (x)")
    embed = Embed(title=message, description="Chances left: {}\n\nWord to guess: {}\n\nLetters guessed: {}".format(
        chances[wrongGuesses], blanks, guesses))
    return embed


@client.command(aliases=['slapjack'], brief="A fast-paced card game all about reaction time.", description="A game for 2 players. Each player gets half of the deck and takes turns placing cards down. Once a jack is played, the first person to 'slap' (type .s) gets to keep that card and all cards played before. The first player to run out of cards loses. Both players must pay 50 coins to play, the winner gets 100 coins.\n\n<user> -- the person you want to play with")
async def slapjackGame(ctx, user):
    # gets the user's tag
    tag = user
    # checks if its an actual tag
    if tag.find("!") != -1:
        tagNumber = tag[3:len(tag) - 1]
        tagNumber = int(tagNumber)
    else:
        tagNumber = -99
    if tagNumber == -99:
        embed = Embed(title="Cannot play game: Not a valid user")
        await ctx.send(embed=embed)
    else:
        embedmain = Embed(title="The SlapJack Costs 50 Coins")
        await ctx.send(embed=embedmain)
        firstresult = getbalance(ctx)
        if firstresult - 50 < 0:
            Noembed = Embed(title="Cannot play game : Insufficient funds")
            await ctx.send(embed=Noembed)
            return

        cursor.execute(update_sql, (firstresult - 50, ctx.message.author.id))
        result = getbalance(ctx)
        embed = Embed(title="Current coin total is:", description="{}".format(result))
        await ctx.send(embed=embed)

        embed1 = Embed(title="Welcome to Slap jack!",
                       description=" Use .p to put a card down. \n Use .s to slap the card. \n Use .q to quit \n REMEMBER 10 IS A JACK")
        await ctx.send(embed=embed1)

        # playing the game
        deck = Deck(1)
        deck.shuffle()

        user1name = ""
        user2name = ""

        user1 = Player(ctx.message.author.id)
        user2 = Player(tagNumber)

        # splits deck in half
        for card in range(0, 40):
            if card % 2 == 0:
                user1.draw(deck)
            if card % 2 != 0:
                user2.draw(deck)


        # the actual game
        cardPile = []

        while user1.numcardsinHand() == 0 or user2.numcardsinHand():
            msg = await client.wait_for('message', timeout=120.0)
            if ".q" == msg.content:
                if user1.numcardsinHand() < user2.numcardsinHand():
                    winner = user2.name
                    winnerName = user2name
                elif user1.numcardsinHand() > user2.numcardsinHand():
                    winner = user1.name
                    winnerName = user1name
                embedwinner = Embed(title="Congrats {} Won the Game".format(winnerName))
                await ctx.send(embed=embedwinner)
                coins = giveCoins(winner, 100)
                embed2 = Embed(title="You won a {} coins!".format(coins))
                await ctx.send(embed=embed2)
                return

            if ".p" == msg.content:
                # put a card down
                if msg.author.id == user1.name:
                    user1name = ctx.message.author.display_name
                    card = user1.dropCard()
                if msg.author.id == user2.name:
                    user2name = msg.author.display_name
                    card = user2.dropCard()
                # shows card in discord
                cardPile.append(card)
                embed = Embed(title=f"card is {card.value} of {card.suit}")
                await ctx.send(embed=embed)

            if ".s" == msg.content:
                # looks for a slap
                if card.value == 10:
                    embed = Embed(title="GOOD JOB, YOU GOT THE JACK...")
                    embed2 = Embed(title="you get all the cards in the pile")
                    if msg.author.id == user1.name:
                        user1.addCards(cardPile)
                    if msg.author.id == user2.name:
                        user2.addCards(cardPile)
                    cardPile = []
                    await ctx.send(embed=embed)
                    await ctx.send(embed=embed2)

                else:
                    embed = Embed(title="WHOOPS, THAT'S NOT A JACK")
                    embed2 = Embed(title="adding 2 cards into the pile")
                    if msg.author.id == user1.name:
                        cardPile.append(user1.dropCard())
                        cardPile.append(user1.dropCard())
                    if msg.author.id == user2.name:
                        cardPile.append(user2.dropCard())
                        cardPile.append(user2.dropCard())
                    await ctx.send(embed=embed)
                    await ctx.send(embed=embed2)
                # CARDS LEFT
                embeduser1 = Embed(title="{}: you have {} cards left".format(user1name, user1.numcardsinHand()))
                embeduser2 = Embed(title="{}: you have {} cards left".format(user2name, user2.numcardsinHand()))
                await ctx.send(embed=embeduser1)
                await ctx.send(embed=embeduser2)
                # if someone has no cards left - the game is over
        if user1.numcardsinHand() == 0 or user2.numcardsinHand():
            if user1.numcardsinHand() == 0:
                winner = user2.name
                winnerName = user2name
            elif user2.numcardsinHand() == 0:
                winner = user1.name
                winnerName = user1name
            embedwinner = Embed(title="Congrats {} Won the Game".format(winnerName))
            await ctx.send(embed=embedwinner)
            coins = giveCoins(winner, 100)
            embed2 = Embed(title="You won a {} coins!".format(coins))
            await ctx.send(embed=embed2)
            return





@client.command(aliases=['buy'], brief="The item shop.", description="Here is where you can spend all the coins you've earned! Type '.shop' with nothing else to see the menu, or '.shop' followed by an item name to buy that item.")
async def shop(ctx, item=None):
    gold = discord.Colour(0xFFD700)
    silver = discord.Colour(0xC0C0C0)
    rolelist = await ctx.guild.fetch_roles()
    check = 0
    for role in rolelist:
        if str(role) == "VIP" or str(role) == "Valued Member":
            check = 1
    if check == 0:
        await ctx.guild.create_role(name="VIP", colour=gold)
        await ctx.guild.create_role(name="Valued Member", colour=silver)
    if item is None:
        # shop menu
        menu = ""
        for x in items:
            curr = items[x]
            menu += str(x) + ":\n" + str(curr[0]) + " coins\n" + str(curr[1]) + "\n" + str(curr[2]) + "\n\n"
        embed = Embed(title="Shop Menu", description=menu)
        await ctx.send(embed=embed)

    elif item == 'balloon':
        result = getbalance(ctx)
        if result < 80:
            embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
            await ctx.send(embed=embed)
            return
        cursor.execute("SELECT balloons FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        temp = cursor.fetchone()
        balloons = temp[0] + 1
        cursor.execute("UPDATE funusers SET balloons = {} where userid = {}".format(balloons, ctx.message.author.id))
        cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(result - 80, ctx.message.author.id))
        result = getbalance(ctx)

        embed = Embed(title="good job you bought a balloon",
                      description="Current coin total: {}\nCurrent balloon total: {}".format(result, balloons))

        await ctx.send(embed=embed)

    elif item == 'vm':
        result = getbalance(ctx)
        if result < 10000:
            embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
            await ctx.send(embed=embed)
            return
        cursor.execute("SELECT vm FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        temp = cursor.fetchone()
        if temp[0] == 1:
            embed = Embed(title="You already have this title...")
            await ctx.send(embed=embed)
            return
        cursor.execute("UPDATE funusers SET vm = {} where userid = {}".format(1, ctx.message.author.id))
        cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(result - 10000, ctx.message.author.id))

        member = ctx.message.author
        role = "Valued Member"
        await member.add_roles(discord.utils.get(member.guild.roles, name=role))

        result = getbalance(ctx)

        embed = Embed(title="good job you bought the valuable member role",
                      description="Current coin total: {}\n".format(result))
        await ctx.send(embed=embed)

    # ACTUALLY ADD THE ROLE

    elif item == 'vip':
        result = getbalance(ctx)
        if result < 50000:
            embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
            await ctx.send(embed=embed)
            return
        cursor.execute("SELECT vip FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        temp = cursor.fetchone()
        if temp[0] == 1:
            embed = Embed(title="You already have this title...")
            await ctx.send(embed=embed)
            return
        cursor.execute("UPDATE funusers SET vip = {} where userid = {}".format(1, ctx.message.author.id))
        cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(result - 50000, ctx.message.author.id))

        member = ctx.message.author
        role = "VIP"
        await member.add_roles(discord.utils.get(member.guild.roles, name=role))

        result = getbalance(ctx)

        embed = Embed(title="good job you bought the VIP role",
                      description="Current coin total: {}\n".format(result))
        await ctx.send(embed=embed)

    # ACTUALLY ADD THE ROLE

    elif item == 'mb':
        result = getbalance(ctx)
        if result < 100:
            embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
            await ctx.send(embed=embed)
            return
        cursor.execute("UPDATE funusers SET coins = {} where userid = {}".format(result - 100, ctx.message.author.id))
        rand = random.randint(0, 100)
        if rand < 14:
            cursor.execute("SELECT balloons FROM funusers WHERE userid = {}".format(ctx.message.author.id))
            temp = cursor.fetchone()
            balloons = temp[0] + 1
            cursor.execute(
                "UPDATE funusers SET balloons = {} where userid = {}".format(balloons, ctx.message.author.id))
            temp = getbalance(ctx)
            embed = Embed(title="You got a Balloon!", description=f"You now have {balloons} balloons!\n"
                                                                  f"You now have {temp} coins")
            await ctx.send(embed=embed)
        elif rand == 100:
            cursor.execute("UPDATE funusers SET coins = {} where "
                           "userid = {}".format(result + 500, ctx.message.author.id))
            cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
            temp = cursor.fetchone()
            embed = Embed(title="You got the Lucky Chest!", description=f"You earned 500 coins!\n"
                                                                        f"You now have {temp[0]} coins")
            await ctx.send(embed=embed)

        else:
            number = random.randint(50, 200)
            cursor.execute("UPDATE funusers SET coins = {} where "
                           "userid = {}".format(result + number, ctx.message.author.id))
            cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
            temp = cursor.fetchone()
            embed = Embed(title="The fates have rolled and....", description=f"You earned {number} coins!\n"
                                                                             f"You now have {temp[0]} coins")
            await ctx.send(embed=embed)
    # roll to see what they get

    elif item == 'daily':

        # check which multiplier they have and see if they can afford the next
        cursor.execute("SELECT daily FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        temp = cursor.fetchone()
        if temp[0] == 1.0:
            result = getbalance(ctx)
            if result < 1000:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET daily = {} where userid = {}".format(1.5, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 1000, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 1.5x your daily income.")
            await ctx.send(embed=embed)
        if temp[0] == 1.5:
            result = getbalance(ctx)
            if result < 2000:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET daily = {} where userid = {}".format(2.0, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 2000, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 2x your daily income.")
            await ctx.send(embed=embed)
        if temp[0] == 2.0:
            result = getbalance(ctx)
            if result < 5000:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET daily = {} where userid = {}".format(3.0, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 5000, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 3x your daily income.")
            await ctx.send(embed=embed)
        if temp[0] == 3.0:
            embed = Embed(title="Sorry!", description="You already have the maximum upgrade.")
            await ctx.send(embed=embed)

    elif item == 'global':

        cursor.execute("SELECT global FROM funusers WHERE userid = {}".format(ctx.message.author.id))
        temp = cursor.fetchone()
        if temp[0] == 1.0:
            result = getbalance(ctx)
            if result < 1500:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET global = {} where userid = {}".format(1.5, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 1500, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 1.5x your global income."
                                                        " (daily excluded)")
            await ctx.send(embed=embed)
        if temp[0] == 1.5:
            result = getbalance(ctx)
            if result < 3000:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET global = {} where userid = {}".format(2.0, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 3000, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 2x your global income."
                                                        " (daily excluded)")
            await ctx.send(embed=embed)
        if temp[0] == 2.0:
            result = getbalance(ctx)
            if result < 6000:
                embed = Embed(title="Sorry not enough coins!", description="Current coin total: {}".format(result))
                await ctx.send(embed=embed)
                return
            cursor.execute("UPDATE funusers SET global = {} where userid = {}".format(3.0, ctx.message.author.id))
            cursor.execute("UPDATE funusers SET coins = {} where userid = {}"
                           .format(result - 6000, ctx.message.author.id))
            embed = Embed(title="Success!", description="You will now earn 3x your global income."
                                                        " (daily excluded)")
            await ctx.send(embed=embed)
        if temp[0] == 3.0:
            embed = Embed(title="Sorry!", description="You already have the maximum upgrade.")
            await ctx.send(embed=embed)


@client.command(aliases=['throwballoon'], brief="Throw a water balloon at somebody!", description="Must have at least one balloon in your inventory. Can be bought from the shop for 80 coins.")
async def throwwaterballoon(ctx, user):
    # gets the user's tag
    tag = user
    # checks if its an actual tag
    if tag.find("!") != -1:
        tagNumber = tag[3:len(tag) - 1]
        tagNumber = int(tagNumber)
    else:
        tagNumber = -99
    if tagNumber == -99:
        embed = Embed(title="Cannot throw balloon: Not a valid user")
        await ctx.send(embed=embed)
        return
    # check if the user has a balloon

    cursor.execute("SELECT balloons FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    temp = cursor.fetchone()
    if (temp[0] == 0):
        embed = Embed(title="Cannot throw balloon: User does not own any balloons")
        await ctx.send(embed=embed)
        return

    # if user has balloon decrements number of balloons a user has
    balloons = temp[0] - 1
    cursor.execute("UPDATE funusers SET balloons = {} where userid = {}".format(balloons, ctx.message.author.id))

    # actually throwing a balloon at someone
    await ctx.send(f"PONG {user}")
    await ctx.send(file=discord.File('waterballoon.gif'))


#client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.cHZlrlH6jsYS7nkjVgBVnshM2JU')
