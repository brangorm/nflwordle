import json
import csv
import re
import urllib.request
import ssl
from bs4 import *
from random import randrange

SEARCH = "age"

fhand = open("data/inputData.csv")
players = list(csv.reader(fhand))
ssl._create_default_https_context = ssl._create_unverified_context
abbrevs = {
    "Arizona Cardinals" : "ARI",
    "Atlanta Falcons" : "ATL",
    "Baltimore Ravens" : "BAL",
    "Buffalo Bills" : "BUF",
    "Carolina Panthers" : "CAR",
    "Chicago Bears" : "CHI",
    "Cincinnati Bengals" : "CIN",
    "Cleveland Browns" : "CLE",
    "Dallas Cowboys" : "DAL",
    "Denver Broncos" : "DEN",
    "Detroit Lions" : "DET",
    "Green Bay Packers" : "GB",
    "Houston Texans" : "HOU",
    "Indianapolis Colts" : "IND",
    "Jacksonville Jaguars" : "JAC",
    "Kansas City Chiefs" : "KC",
    "Miami Dolphins" : "MIA",
    "Minnesota Vikings" : "MIN",
    "New England Patriots" : "NE",
    "New Orleans Saints" : "NO",
    "New York Giants" : "NYG",
    "New York Jets" : "NYJ",
    "Las Vegas Raiders" : "LV",
    "Oakland Raiders" : "LV",#####
    "Philadelphia Eagles" : "PHI",
    "Pittsburgh Steelers" : "PIT",
    "Los Angeles Chargers" : "LAC",
    "San Diego Chargers" : "LAC",#####
    "San Francisco 49ers" : "SF",
    "Seattle Seahawks" : "SEA",
    "Los Angeles Rams" : "LAR",
    "St. Louis Rams" : "LAR",#####
    "Tampa Bay Buccaneers" : "TB",
    "Tennessee Titans" : "TEN",
    "Washington Football Team" : "WAS",
    "Washington Redskins" : "WAS"#####
}
bads = {
"najee-harris": "najee-harris-x2665",
"elijah-mitchell" : "elijah-mitchell-2",
"michael-carter" : "michael-carter-3",
"michael-badgley" : "mike-badgley",
"deonte-harty" : "deonte-harris",
"nick-westbrook-ikhine" : "nick-westbrook",
"trey-lance" : "trey-lance-x9749",
"henry-ruggs" : "henry-ruggs-iii",
"joshua-palmer" : "josh palmer",
"p-j-walker" : "phillip-walker",
"scotty-miller" : "scott-miller"



}
def encode(string):
    string = string.replace(" III", "").replace(" II", "").replace(" IV", "").replace(" Jr.", "").replace(" Sr.", "").lower()
    
    retStr = string.replace(". ", "-").replace(" ", "-").replace("'", "-").replace(".","-")
    if retStr in bads: return bads[retStr]
    return retStr
    
successes = 0
for i in range(1,509):
    #try:
    print("=========================")
    player = players[i][1]
    playerRow = players[i]
    url = ""
    if SEARCH == "teams": url = "https://www.nfl.com/players/" + encode(player) + "/stats/career"
    elif SEARCH == "age": url = "https://www.nfl.com/players/" + encode(player) + "/"
    print(url)
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    data = mybytes.decode("utf8")
    
    soupd = BeautifulSoup(data, features="html.parser")
    
    if SEARCH == "teams":
        table_class = '''d3-o-table d3-o-standings--detailed d3-o-table--sortable {sortlist: [[0,1]], debug: true}'''
        
        teamtable = soupd.find("table", {"class": table_class})
        if not teamtable:
            print("Failed on " + player)
            continue
        #print(teamtable)
        newTeams = []
        for row in teamtable.find_all("tr"):
            if not row.find("td"): continue
            #print(row)
            team = row.find_all("td")[1].text.strip()
            if not abbrevs.get(team):
                print("*************************************TEAM DOES NOT EXIST " + team + " *********************************")
            if abbrevs.get(team) not in newTeams:
                newTeams.append(abbrevs.get(team))
                print(team)
        newTeams = ", ".join(newTeams)
        playerRow.append(newTeams)
        csv.writer(open("data/pool3.csv", "a", newline='')).writerow(playerRow)
    elif SEARCH == "age": #Really age and height and college
        #The info table is split into two "ul" sections. First one contains age and physicals, second one contains age and college.
        table1_class = '''d3-o-list nfl-c-player-info__physical-data''' #Class for "ul" section that includes height and physicals
        table2_class = '''d3-o-list nfl-c-player-info__career-data''' #Class for "ul" section that includes age and college
        table1 = soupd.find("ul", {"class": table1_class})
        table2 = soupd.find("ul", {"class": table2_class})
        if not (table1 and table2):
            print("Failed on " + player)
            csv.writer(open("data/bads.csv", "a", newline='')).writerow(playerRow)
            continue
        row = list()
        value_class = '''nfl-c-player-info__value'''
        height = table1.find_all("div", {"class":value_class})[0].text.strip()
        years = table2.find_all("div", {"class":value_class})[0].text.strip()
        college = table2.find_all("div", {"class":value_class})[1].text.strip()
        age = table2.find_all("div", {"class":value_class})[2].text.strip()
        print("Height: " + height)
        print("Age: " + age)
        print("College: " + college)
        print("Years in NFL: " + years)
        successes += 1
        print("Predicted number of manual edits: " + str(round(float(508) - ((float(successes) / float(i)) * float(508)))))
        print("Progress: " + str(i) + " / 508")
        playerRow.append(age)
        playerRow.append((" " + height)) #required so Excel doesnt format as date
        playerRow.append(college)
        playerRow.append(years)
        csv.writer(open("data/outputData.csv", "a", newline='')).writerow(playerRow)
    #except:
    #    print("Failed on player" + players[i][1])
    #    continue