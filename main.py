import discord
import sqlite3
from discord.ext import commands
from discord import Embed
import csv
import random

items = {'balloon': 80, 'valueableMember': 10000, 'vip': 50000, 'randomCoins': 100, 'dailyMultiplier': [1000, 2000, 5000], 'globalMultiplier': [1500, 3000, 6000]}


def db_connect():
    return sqlite3.connect(r'C:\Users\Nathan\Documents\CS321\database.sqlite3')


bot = commands.Bot(command_prefix='$')

connection = db_connect()
cursor = connection.cursor()
userData = """
CREATE TABLE funusers (
    userid integer PRIMARY KEY,
    coins integer NOT NULL),
	balloons INTEGER,
	vm INTEGER,
	vip INTEGER,
	daily REAL,
	global REAL"""
# cursor.execute(userData)
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

    def dropCard(self):
        return self.hand.pop()

    def numcardsinHand(self):
        x = 1
        for i in self.hand:
            x += 1
        return x

    def addCards(self, pile):
        self.hand.append(pile)

    def showHand(self):
        x = 1
        for i in self.hand:
            print(f"card {x} is {i.value} of {i.suit}")
            x += 1
        return


# helper function to get users balance of coins
def getbalance(ctx):
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(ctx.message.author.id))
    result = cursor.fetchone()
    return result[0]


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
@commands.has_permissions(administrator=True)
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


@client.command(aliases=['black'])
async def blackjack(ctx, money: int):
    result = getbalance(ctx)

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
                    cursor.execute(update_sql, (money * 3, ctx.message.author.id))
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
                cursor.execute(update_sql, (money * 3, ctx.message.author.id))
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


@client.command(aliases=['unscramble'])
async def unscrambleGame(ctx):
    embedstart = Embed(title="Starting unscramble game")
    await ctx.send(embed=embedstart)
    embedmain = Embed(title="The Unscramble Game Costs 50 Coins")
    firstresult = getbalance(ctx)
    if firstresult - 50 < 0:
        Noembed = Embed(title="Cannot play game : Insufficient funds")
        await ctx.send(embed=Noembed)
        return
    cursor.execute(update_sql, (firstresult - 50 , ctx.message.author.id))
    result = getbalance(ctx)
    embed = Embed(title="Current coin total is:", description="{}".format(result))
    await ctx.send(embed=embed)
    embed1 = Embed(title="Starting unscramble game: \n Remember to put a .guess in front of your guess!")
    originalWord = getWord()
    scrammbledWord = scrammble(originalWord)
    embed1.add_field(name="UNSCRAMBLE: ", value="{}".format(scrammbledWord), inline=False)
    await ctx.send(embed=embed)
    await ctx.send(embed=embedmain)
    await ctx.send(embed=embed1)


    x = {'value': 3}

    @client.command(aliases=['guess'])
    async def unscrambleGuess(ctx, arg):
        totalguess = x['value']
        if arg == originalWord:
            embed1 = Embed(title="Good job you got the right word")
            await ctx.send(embed=embed1)
            embed2 = Embed(title="You won a 100 coins!")
            await ctx.send(embed=embed2)
            result = getbalance(ctx)
            cursor.execute(update_sql, (result + 100, ctx.message.author.id))
            result = getbalance(ctx)
        if arg != originalWord and totalguess != 0:
            await ctx.channel.send("Wrong guess! Try again ")
            x['value'] -= 1
            totalguess = x['value']
            await ctx.channel.send("Only {} chances left".format(totalguess))
        if totalguess == 0:
            await ctx.channel.send("All out of guesses! Good luck next time!")


@client.command(brief="The classic game of hangman.", description="")
async def hangman(ctx):
    #checks if the user has enough coins
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
    #used later to fill in the blanks
    blanksList = list(blanks)

    start = hangmanPrint("Game start!", wrongGuesses, blanks, guesses)
    await ctx.send(embed = start)

    while done == 0:

        def check(m):
            if (len(m.content) > 1):
                return False
            else:
                return True

        response = await client.wait_for('message', check = check)

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
            cursor.execute(update_sql, (result + 100, ctx.message.author.id))
            embed = hangmanPrint("Congrats, you won and earned 100 coins!", wrongGuesses, blanks, guesses)
            await ctx.send(embed=embed)
            break
        else:
            embed = hangmanPrint("Correct! Keep guessing...", wrongGuesses, blanks, guesses)
            await ctx.send(embed=embed)
            continue

def hangmanPrint(message, wrongGuesses, blanks, guesses):
    chances = ("() () () () () ()", "(x) () () () () ()", "(x) (x) () () () ()", "(x) (x) (x) () () ()", "(x) (x) (x) (x) () ()", "(x) (x) (x) (x) (x) ()", "(x) (x) (x) (x) (x) (x)")
    embed = Embed(title=message, description="Chances left: {}\n\nWord to guess: {}\n\nLetters guessed: {}".format(chances[wrongGuesses], blanks, guesses))
    return embed


@client.command(aliases=['slapjack'])
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
                       description=" Use p to put a card down. \n Use j to slap the card. \n Use q to quit \n REMEMBER 10 IS A JACK")
        await ctx.send(embed=embed1)


        # playing the game
        deck = Deck(1)
        deck.shuffle()
        user1 = Player(ctx.message.author.id)
        user2 = Player(tagNumber)

        # splits deck in half
        for card in range(0, 40):
            if card % 2 == 0:
                user1.draw(deck)
            if card % 2 != 0:
                user2.draw(deck)

        # DELETE THIS LATER -- JUST FOR ME TO KNOW EACH PERSONS CARDS
        #user1.showHand()
        #print("--------------")
        #user2.showHand()
        # the actual game
        cardPile = []

        while user1.numcardsinHand() != 0 or user2.numcardsinHand() != 0:
            msg = await client.wait_for('message', timeout=60.0)
            # gets a card from that users pile
            if msg.content == "p":
                if msg.author.id == user1.name:
                    print("USER 1")
                    card = user1.dropCard()
                if msg.author.id == user2.name:
                    print("USER 2")
                    card = user2.dropCard()
                # shows card in discord
                cardPile.append(card)
                embed = Embed(title=f"card is {card.value} of {card.suit}")
                await ctx.send(embed=embed)
                #looks for a slap
                msg2 = await client.wait_for('message', timeout=2.0)
                if msg2.content == "j":
                    if card.value == 10:
                        embed = Embed(title="GOOD JOB, YOU GOT THE JACK...")
                        embed2 = Embed(title="you get all the cards in the pile")
                        if msg2.author.id == user1.name:
                            user1.addCards(cardPile)
                        if msg2.author.id == user2.name:
                            user2.addCards(cardPile)
                        cardPile = []
                        await ctx.send(embed=embed)
                        await ctx.send(embed=embed2)

                    else:
                        embed = Embed(title="WOOPS, THAT'S NOT A JACK")
                        embed2 = Embed(title= "adding 2 cards into the pile")
                        if msg2.author.id == user1.name:
                            cardPile.append(user1.dropCard())
                            cardPile.append(user1.dropCard())
                        if msg2.author.id == user2.name:
                            cardPile.append(user2.dropCard())
                            cardPile.append(user2.dropCard())
                        await ctx.send(embed=embed)
                        await ctx.send(embed=embed2)
                    # CARDS LEFT
                    embeduser1 = Embed(title="{}: you have {} cards left".format(user1.name, user1.numcardsinHand()))
                    embeduser2 = Embed(title="{}: you have {} cards left".format(user2.name, user2.numcardsinHand()))
                    await ctx.send(embed=embeduser1)
                    await ctx.send(embed=embeduser2)
                    # if someone has no cards left - the game is over
                    if user1.numcardsinHand() == 0 or user2.numcardsinHand():
                        if user1.numcardsinHand() == 0:
                            winner = user2.name
                        elif user2.numcardsinHand() == 0:
                            winner = user1.name
                        embedwinner = Embed(title="Congrats {} Won the Game".format(winner))
                        await ctx.send(embed=embedwinner)
                        embed2 = Embed(title="You won a 100 coins!")
                        await ctx.send(embed=embed2)
                        # add money to winner
                        cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format(winner))
                        ans = cursor.fetchone()
                        result = ans[0]
                        cursor.execute(update_sql, (result + 100, ctx.message.author.id))

            #if msg.content == "q":
             #   # do the quit stuff



client.run('NzY0MTgwMzU1MzU0ODUzNDE2.X4Cgag.FjIBu-8Bk4eOLMpViazU242koZg')
