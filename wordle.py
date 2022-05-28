import json
import csv
import re
from random import randrange, sample
from enum import Enum
from profanity_check import predict, predict_prob

fhand = open("data/pool.csv")
players = list(csv.reader(fhand))
feedhand = open('app/static/logs/feed.txt')
feedhandW = open('app/static/logs/feed.txt', 'a')


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
"Years in NFL" : 11,
"Stat" : 12
}

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

diffs = {
"Easy" : range(1, 76),
"Medium" : range(30, 150),
"Hard" : range(150, 300),
"Extreme" : range(300, 508),
"Include all players" : range(1, 508)
}

def isProfanity(name):
    return predict([name])[0]

def hasData(restr):
    for category in ["conField", "divField", "posField"]:
        if (restr[category] is not None) and (restr[category] != ["All"]) and (len(restr[category]) > 0):
            return True
    return False

def get_color(guessCategory):
    result = guessCategory[0]
    mappings = {"CORRECT" : "green", "INCORRECT" : "red", "ALMOST" : "yellow", "TOO_HIGH" : "orange", "TOO_LOW" : "blue", "NA" : "gray"}
    return mappings.get(result)

def clearSession(session):
    for item in ['answer', 'isHard', 'guesses', 'found']:
        if item in session: session.pop(item)

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
    
def std(string):
    string = string.replace(" III", "").replace(" II", "").replace(" IV", "").replace(" Jr.", "").replace(" Sr.", "").replace("Scott Miller", "Scotty Miller").replace("Michael Badgley", "Mike Badgley")
    expr = re.compile('[^a-zA-Z]')
    return expr.sub('', string).lower()

def verifyRestr(pos, team, attr):
    valid = True
    if attr[0] == "NFC" or attr[0] == ["AFC"]:
        if getCon(team) not in attr: valid = False
    elif attr[0].startswith("NFC") or attr[0].startswith("AFC"):
        if getDiv(team) not in attr: valid = False
    else:
        if pos not in attr: valid = False
    #if not valid:
        #print("Verification failed for this data: ")
        #print(str(pos) + str(team) + str(attr))
    return valid
   

def decide(diff, restr):
    playerPool = []
    player = None
    for row in players[1:]:
        valid = True
        pos = row[3]
        team = row[2]
        for category in ["conField", "divField", "posField"]:
            if (restr.get(category) is not None) and (restr[category] != ["All"]) and (len(restr[category]) > 0):
                if not verifyRestr(pos, team, restr[category]):
                    valid = False
                    break
        if valid: playerPool.append(row[1])
    if not playerPool:
        print("These restrictions were invalid:")
        print(restr)
        return None
    rang = len(playerPool)
    if restr:
        index = randrange(0,rang)
    else:
        index = sample(diffs[diff], 1)[0]
    player = playerPool[index]
    return player


def isValidGuess(guess):
    for row in players:
        if std(row[1]) == std(guess):
            return True
    return False

def isValidRestr(restr):
    if not decide("Easy", restr): return False
    else: return True

def getPastTeams(player):
    for row in players:
        if std(row[1]) == std(player):
            return row[7]
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

def do_guess(answer, guess):
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
    
    answerPos = getCell(answer, "Position")
    guessPos = getCell(guess, "Position")
    
    answerTeam = getCell(answer, "Team")
    guessTeam = getCell(guess, "Team")
    
    answerConf = getCon(answerTeam)
    guessConf = getCon(guessTeam)
    
    answerDiv = getDiv(answerTeam)
    guessDiv = getDiv(guessTeam)
    
    answerPast = getCell(answer, "Teams").split(",")
    
    answerAge = getCell(answer, "Age")
    guessAge = getCell(guess, "Age")
    
    answerHeight = getCell(answer, "Height").strip()
    guessHeight = getCell(guess, "Height").strip()
    
    answerCollege = getCell(answer, "College")
    guessCollege = getCell(guess, "College")
    
    answerYears = getCell(answer, "Years in NFL")
    guessYears = getCell(guess, "Years in NFL")
    
    answerStat = getCell(answer, "Stat")
    guessStat = getCell(guess, "Stat")
    
    if std(answer) == std(guess):
        data["Found"] = True
    if answerPos != guessPos:
        data["Position"] = ["INCORRECT", guessPos]
    if answerPos == guessPos:
        data["Position"] = ["CORRECT", guessPos]
        
        mappings = {
        "QB" : "Passing Yds.",
        "WR" : "Receiving Yds.",
        "RB" : "Rushing Yds.",
        "TE" : "Receiving Yds.",
        "K" : "Fantasy Pts."
        }
        pos = answerPos
        label = mappings.get(pos)
        if float(answerStat) > float(guessStat):
            data["Stat"] = ["TOO_LOW", guessStat, label]
        elif float(answerStat) < float(guessStat):
            data["Stat"] = ["TOO_HIGH", guessStat, label]
        else:
            data["Stat"] = ["CORRECT", guessStat, label]   
        
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
    
# Schema:
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
