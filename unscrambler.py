import csv
import random


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

def scrammble(word):
    # scrambles the word
    l = list(word)
    random.shuffle(l)
    newWord = ''.join(l)
    print(newWord)
    return newWord

def game(originalWord, scrammbledWord):
    # total number of guesses = 3
    guess = 0
    
def main():
   originalWord =  getWord()
   scrammbledWord = scrammble(originalWord)


if __name__ == '__main__':
    main()
