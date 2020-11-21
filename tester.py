# A tester that checks if our database is working
import asyncio

import discord
from discord.utils import get
import sqlite3
from discord.ext import commands
from discord import Embed
import csv
import random
from main import getWord



def db_connect():
    return sqlite3.connect(r'/Users/nikita/Documents/GitHub/CS321-Project-Discord-Bot\database.sqlite3’')

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


def main():
    db_connect()
    createUser()
    testsetCoins()
    testaddCoins()
    testremoveCoins()
    testbuyballoon()
    testgetWord()
    testsendMoney()



#test the code in on message to make sure that a newuser gets created
def createUser():
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format("21"))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(funuser_sql, ("21", 0, 0, 0, 0, 1.0, 1.0))
    testCreateUser()
def testCreateUser():
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format("21"))
    result = cursor.fetchone()
    if result is None:
        return
    else:
        print("Test 1: Create User Passed")
        return

# tests the code that updates coins
def testsetCoins():
  cursor.execute(update_sql, (50, "21"))
  cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
  result = cursor.fetchone()
  if (result[0]== 50):
      print("Test 2: Updating Coins")

# test if coins are added to current money
def testaddCoins():
    coins = 100
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    temp = cursor.fetchone()
    result = temp[0]
    cursor.execute(update_sql, (result + coins, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    ans = cursor.fetchone()
    if (ans[0] == 150):
      print("Test 3: Adding Coins")

# test if coins are removed to current money
def testremoveCoins():
    coins = 100
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    temp = cursor.fetchone()
    result = temp[0]
    cursor.execute(update_sql, (result - coins, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    ans = cursor.fetchone()
    if (ans[0] == 50):
      print("Test 4: Removes Coins")

# tests if a user can buy a balloon
def testbuyballoon():
    cursor.execute(update_sql, (500, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    temp = cursor.fetchone()
    result = temp[0]
    price = 80
    cursor.execute(update_sql, (result - price, "21"))
    cursor.execute("SELECT balloons FROM funusers WHERE userid = {}".format("21"))
    temp = cursor.fetchone()
    balloons = temp[0] + 1
    cursor.execute("UPDATE funusers SET balloons = {} where userid = {}".format(balloons, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    resultmoney = cursor.fetchone()
    cursor.execute("SELECT balloons FROM funusers WHERE userid = {}".format("21"))
    resultballoons = cursor.fetchone()
    if (resultmoney[0] == 420 and resultballoons[0] == 1):
        print("Test 5:  Buys Balloons")

# tests if getword function gets a word
def testgetWord():
    word = getWord(5)
    if len(word) == 5:
        print("Test 6:  Get Word")

# send money
def testsendMoney():
    cursor.execute("SELECT userid FROM funusers WHERE userid = {}".format("22"))
    result = cursor.fetchone()
    if result is None:
        cursor.execute(funuser_sql, ("22", 0, 0, 0, 0, 1.0, 1.0))
    cursor.execute(update_sql, (100, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    result = cursor.fetchone()
    coins = 50
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    temp = cursor.fetchone()
    result = temp[0]
    cursor.execute(update_sql, (result - coins, "21"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    ans = cursor.fetchone()
    coins = 50
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("22"))
    temp = cursor.fetchone()
    result = temp[0]
    cursor.execute(update_sql, (result + coins, "22"))
    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("22"))
    ans = cursor.fetchone()

    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("21"))
    person1 = cursor.fetchone()

    cursor.execute("SELECT coins FROM funusers WHERE userid = {}".format("22"))
    person2 = cursor.fetchone()

    if (person1[0] == 50 and person2[0] == 50):
        print("Test 7:  Send Money")






if __name__ == '__main__':
    main()
