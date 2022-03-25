from wordle import players, std, getPlayerData
import csv
fhand = csv.writer(open("data/wStat.csv", "a", newline=''))
for row in players[1:]:
    player = row[1]
    pos = row[3]
    data = getPlayerData(player)
    maps = {
    "QB" : "PassingYDS",
    "WR" : "ReceivingYDS",
    "RB" : "RushingYDS",
    "TE" : "ReceivingYDS",
    "K" : "TotalPoints"
    }
    stat = data[maps.get(pos)]
    if not stat:
        stat = "0" #This is crazy. Brandon Powell has 0 receptions and got all his points from a KR TD.
        print(player)# and Andy Janovich has 2 total rushes for 0 yards AND A TOUCHDOWN on the year.
    
    
    newRow = row
    newRow.append(stat)
    fhand.writerow(newRow)
    