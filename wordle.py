import json
import csv
import re
from random import randrange
from enum import Enum

fhand = open("data/pool.csv")
players = list(csv.reader(fhand))
beg = 1
end = 509
columns = { "Rank": 0,
"Player" : 1,
"Team" : 2,
"Position" : 3,
"Points": 4,
"Games" : 5,
"Avg" : 6,
"Teams" : 7,
"Age" : 8,
"Height": 9,
"College" : 10,
"Years in NFL" : 11
}

class Status(Enum):
    CORRECT = 0
    INCORRECT = 1
    ALMOST = 2
    TOO_HIGH = 3
    TOO_LOW = 4
    NA = 5

def get_color(item):
    result = item[0]
    mappings = {"CORRECT" : "green", "INCORRECT" : "red", "ALMOST" : "yellow", "TOO_HIGH" : "orange", "TOO_LOW" : "blue", "NA" : "gray"}
    return mappings.get(result)
# print("Guess the random NFL player. Rules: \n" +
    # "1. Positions: QB, WR, RB, TE \n" +
    # "2. Scored at least 5 fantasy points in 2021 \n" +
    # "3. Capitalization/punctuation doesn't matter, just spell the names right")
# print("Enter difficulty. Press 0 for easy, 1 for medium, 2 for hard, and 3 for EXTREME.")

# try: x = int(input())
# except: x = 4

# if x == 0:
    # end = 128
    # print("Easy difficulty selected.")
# elif x == 1:
    # beg = 128
    # end = 200
    # print("Medium difficulty selected.")
# elif x == 2:
    # beg = 201
    # end = 300
    # print("Hard difficulty selected.")
# elif x == 3:
    # beg = 301
    # print("EXTREME difficulty selected.")
# else:
    # print("Including all players...")
#files = {"WR" : "data/WR_season.json", "RB" : "data/RB_season.json", "TE" : "data/TE_season.json", "QB" : "data/QB_season.json", "K" : "data/K_season.json"}
file = "data/playerData.json"
playerData = json.load(open(file))
conferences = { "NFC" : 
    ["GB", "MIN", "DET", "CHI",
    "TB", "ATL", "CAR", "NO",
    "NYG", "PHI", "DAL", "WAS",
    "LAR", "ARI", "SF", "SEA"
    ]
    ,
    "AFC" : 
    ["PIT", "CLE", "BAL", "CIN",
    "TEN", "HOU", "IND", "JAC",
    "NE", "BUF", "NYJ", "MIA",
    "KC", "LV", "LAC", "DEN"
    ]
}

def isHardPlayer(player):
    i = 0
    for row in players:
        i += 1
        if std(row[1]) == std(player): break
    if i > 300: return True
    else: return False

def getTeam(player):
    for row in players:
        if std(row[1]) == std(player):
            return row[2]
    return None

def getCon(team):
    if team in conferences["NFC"]: return "NFC"
    else: return "AFC"

def getDiv(team):
    conf = getCon(team)
    index = conferences[conf].index(team)
    div = ""
    if index < 4: div = "North"
    elif index < 8: div = "South"
    elif index < 12: div = "East"
    else: div = "West"
    return conf + " " + div
    
# data = list()
# for file in files.values():
    # fhand = open(file)
    # data.extend(json.load(fhand))

# open("data/playerData.json", "w").write(json.dumps(data, indent=4, sort_keys=True))

def std(string):
    string = string.replace(" III", "").replace(" II", "").replace(" IV", "").replace(" Jr.", "").replace(" Sr.", "").replace("Scott Miller", "Scotty Miller").replace("Michael Badgley", "Mike Badgley")
    expr = re.compile('[^a-zA-Z]')
    return expr.sub('', string).lower()


def decide(beg, end):
    index = randrange(beg,end)
    row = players[index]
    player = row[1]
    found = False
    for item in playerData:
        if std(item["PlayerName"]) == std(player):
            return item
    if not found:
        return decide()
        #6 out of 509 players have weird names and are irrelevant anyway: Cedrick Wilson, Michael Badgley, Deonte Hardy, Joshua Palmer, Jody Fortson, JaQuan Hardy


def isValidGuess(guess):
    for row in players:
        if std(row[1]) == std(guess):
            return True
    return False

def getPastTeams(player):
    for row in players:
        if std(row[1]) == std(player):
            return row[7]
    return None
    
def getPlayerData(player):
    for item in playerData:
        if std(item["PlayerName"]) == std(player):
            return item
    print("Could not find player " + player)
    return None

def compareHeight(h1, h2):
    h1Feet = int(h1.split("-")[0])
    h1In = int(h1.split("-")[1])
    h2Feet = int(h2.split("-")[0])
    h2In = int(h2.split("-")[1])
    
    if h1Feet > h2Feet:
        return 1
    elif h1Feet == h2Feet:
        if h1In > h2In: return 1
        elif h1In == h2In: return 0
        else: return -1
    else:
        return -1
        
def getCell(player, stat):
    index = columns[stat]
    for row in players:
        if std(row[1]) == std(player):
            return row[index]
    return None

def receiveValidGuess():
    print("Enter your guess: ")
    guess = input()
    if guess == "":
        return "win"
    stdGuess = std(guess)
    if not isValidGuess(stdGuess):
        print("Not a valid player")
        return receiveValidGuess()
    return guess

def do_guess(answerData, guessData):
    answer = answerData["PlayerName"]
    guess = ""
    try:
        guess = guessData["PlayerName"]
    except:
        return None#print("THIS IS AN ERROR. YOUR PLAYER'S NAME HAS ANOTHER INTERPRETATION. TRY IT.")
    
    data = {
    "Found" : False,
    "Name" : guess,
    "Conference" : ["NA", "ConferenceName"],
    "Division" : ["NA", "DivisionName"],
    "Team" : ["NA", "TeamName"],
    "Position" : ["NA", "PosName"],
    "Stat" : ["NA", "N/A", "N/A"], #First one value, second one name of stat
    "Height" : ["NA", "HeightValue"],
    "Age" : ["NA", "AgeValue"],
    "College" : ["NA", "N/A"]
    }
    
    answerTeam = getTeam(answer)
    guessTeam = getTeam(guess)
    
    answerConf = getCon(answerTeam)
    guessConf = getCon(guessTeam)
    
    answerDiv = getDiv(answerTeam)
    guessDiv = getDiv(guessTeam)
    
    answerPast = getPastTeams(answer).split(",")
    
    answerAge = getCell(answer, "Age")
    guessAge = getCell(guess, "Age")
    
    answerHeight = getCell(answer, "Height")
    guessHeight = getCell(guess, "Height")
    
    answerCollege = getCell(answer, "College")
    guessCollege = getCell(guess, "College")
    
    answerYears = getCell(answer, "Years in NFL")
    guessYears = getCell(guess, "Years in NFL")
    
    if answerData["PlayerName"] == guessData["PlayerName"]:
        data["Found"] = True
    if answerData["Pos"] != guessData["Pos"]:
        data["Position"] = ["INCORRECT", guessData["Pos"]]
    if answerData["Pos"] == guessData["Pos"]:
        data["Position"] = ["CORRECT", guessData["Pos"]]
        
        pos = answerData["Pos"]
        if pos == "QB":
            if float(answerData["PassingYDS"]) > float(guessData["PassingYDS"]):
                data["Stat"] = ["TOO_LOW", guessData["PassingYDS"], "Passing Yds."]
            elif float(answerData["PassingYDS"]) < float(guessData["PassingYDS"]):
                data["Stat"] = ["TOO_HIGH", guessData["PassingYDS"], "Passing Yds."]
            else:
                data["Stat"] = ["CORRECT", guessData["PassingYDS"], "Passing Yds."]
        
        elif pos == "WR":
            if float(answerData["ReceivingYDS"]) > float(guessData["ReceivingYDS"]):
                data["Stat"] = ["TOO_LOW", guessData["ReceivingYDS"], "Receiving Yds."]
            elif float(answerData["ReceivingYDS"]) < float(guessData["ReceivingYDS"]):
                data["Stat"] = ["TOO_HIGH", guessData["ReceivingYDS"], "Receiving Yds."]
            else:
                data["Stat"] = ["CORRECT", guessData["ReceivingYDS"], "Receiving Yds."]
                
        elif pos == "RB":
            if float(answerData["RushingYDS"]) > float(guessData["RushingYDS"]):
                data["Stat"] = ["TOO_LOW", guessData["RushingYDS"], "Rushing Yds."]
            elif float(answerData["RushingYDS"]) < float(guessData["RushingYDS"]):
                data["Stat"] = ["TOO_HIGH", guessData["RushingYDS"], "Rushing Yds."]
            else:
                data["Stat"] = ["CORRECT", guessData["RushingYDS"], "Rushing Yds."]
                
        elif pos == "TE":
            if float(answerData["ReceivingYDS"]) > float(guessData["ReceivingYDS"]):
                data["Stat"] = ["TOO_LOW", guessData["ReceivingYDS"], "Receiving Yds."]
            elif float(answerData["ReceivingYDS"]) < float(guessData["ReceivingYDS"]):
                data["Stat"] = ["TOO_HIGH", guessData["ReceivingYDS"], "Receiving Yds."]
            else:
                data["Stat"] = ["CORRECT", guessData["ReceivingYDS"], "Receiving Yds."]
        
        elif pos == "K":
            if float(answerData["TotalPoints"]) > float(guessData["TotalPoints"]):
                data["Stat"] = ["TOO_LOW", guessData["TotalPoints"], "Fantasy Pts."]
            elif float(answerData["TotalPoints"]) < float(guessData["TotalPoints"]):
                data["Stat"] = ["TOO_HIGH", guessData["TotalPoints"], "Fantasy Pts."]
            else:
                data["Stat"] = ["CORRECT", guessData["TotalPoints"], "Fantasy Pts."]
        
        
        
    if answerTeam == guessTeam:
        data["Team"] = ["CORRECT", guessTeam]
        data["Division"] = ["CORRECT", guessDiv]
        data["Conference"] = ["CORRECT", guessConf]
    elif answerDiv == guessDiv:
        data["Team"] = ["ALMOST", guessTeam]
        data["Division"] = ["CORRECT", guessDiv]
        data["Conference"] = ["CORRECT", guessConf]
    elif answerConf == guessConf:
        data["Team"] = ["INCORRECT", guessTeam]
        data["Division"] = ["INCORRECT", guessDiv]
        data["Conference"] = ["CORRECT", guessConf]
    else:
        data["Team"] = ["INCORRECT", guessTeam]
        data["Division"] = ["INCORRECT", guessDiv]
        data["Conference"] = ["INCORRECT", guessConf]
    if answerTeam != guessTeam and guessTeam in answerPast:
        data["Team"] = ["ALMOST", guessTeam]
    
    if (int(guessAge) > int(answerAge)):
        data["Age"] = ["TOO_HIGH", str(guessAge)]
    elif (int(guessAge) < int(answerAge)):
        data["Age"] = ["TOO_LOW", str(guessAge)]
    else:
        data["Age"] = ["CORRECT", str(guessAge)]
        
    heightCompare = compareHeight(guessHeight, answerHeight)
    if (heightCompare > 0):
        data["Height"] = ["TOO_HIGH", (guessHeight + '''"''')]
    elif (heightCompare < 0):
        data["Height"] = ["TOO_LOW", (guessHeight + '''"''')]
    else:
        data["Height"] = ["CORRECT", (guessHeight + '''"''')]
    
    if guessCollege == answerCollege:
        data["College"] = ["CORRECT", guessCollege]
    
    return data
    
# answerData = decide()
# found = False
# guesses = 0
# #print(answerData["PlayerName"])
# while not found:
    # guess = receiveValidGuess()
    # guesses += 1
    # if guess == "win":
        # print(answerData["PlayerName"])
        # quit()
    # guessData = getPlayerData(std(guess))
    # found = do_guess(answerData, guessData)

# print("You got it in " + str(guesses) + " guesses")




#print(playerData)



#print(json.dumps(data, indent=4, sort_keys=True))