from pathlib import Path
import os
from datetime import datetime

def WriteTsv(data, filepath):
    data = ["\t".join([str(y) for y in x]) + "\n" for x in data]
    with open(filepath, "w", encoding="utf-8") as outfile:
        outfile.writelines(data)

def find_first_ascii_index(string):
  for i, char in enumerate(string):
    if ord(char) < 128:
      return i
  return -1  # Return -1 if no ASCII character is found

def CalcLikesGiven(likesMap):
    likesCountMap = {}
    for author, likes in likesMap.items():
        if author not in likesCountMap:
            likesCountMap[author] = {}
            for emoji, messages in likes.items():
                if emoji not in likesCountMap[author]:
                    likesCountMap[author][emoji] = 0
                if "overall" not in likesCountMap[author]:
                    likesCountMap[author]["overall"] = 0
                for message in messages:
                    likesCountMap[author][emoji] += 1
                    likesCountMap[author]["overall"] += 1
    return likesCountMap

def PreProcessLikesMap(data):
    likesMap = {}
    for line in data:
        likesStr = line[4]
        if len(likesStr) == 0:
            continue
        likesSpl = likesStr.split("%%")
        if likesSpl is None or len(likesSpl) == 0:
            continue
        for likeStr in likesSpl:
            emojiEndIdx = find_first_ascii_index(likeStr)
            emoji = likeStr[:emojiEndIdx]
            parenthesisIdx = likeStr.index(" (")
            author = likeStr[emojiEndIdx:parenthesisIdx]
            timestamp = likeStr[parenthesisIdx+2:-1]
            if author not in likesMap:
                likesMap[author] = {}
            if emoji not in likesMap[author]:
                likesMap[author][emoji] = []
            likesMap[author][emoji].append(line)
    return likesMap

def CalcTotalPosts(resultsPath, data, likesMap):
    totalTexts = len([x for x in data if len(x[2]) > 0])
    totalPictures = len([x for x in data if "/photos/" in x[3]])
    totalVideos = len([x for x in data if "/videos/" in x[3]])
    totalVoice = len([x for x in data if "/audio/" in x[3]])

    totalReactions = 0
    for person, emojiMap in likesMap.items():
        for emoji, reactions in emojiMap.items():
            totalReactions += len(reactions)

    result = [
        ["Texts", totalTexts],
        ["Pictures", totalPictures],
        ["Videos", totalVideos],
        ["Voice", totalVoice],
        ["Reactions", totalReactions],
    ]
    WriteTsv(result, resultsPath / "TotalPosts.tsv")

    textsByDayMap = {}
    for line in data:
        if len(line[2]) == 0:
            continue
        dt = datetime.strptime(line[0], "%b %d, %Y %I:%M:%S %p")
        date = dt.strftime("%Y-%m-%d")
        if date not in textsByDayMap:
            textsByDayMap[date] = 0
        textsByDayMap[date] += 1

    textsByDay = [[k, v] for k, v in textsByDayMap.items()]
    textsByDay = sorted(textsByDay, key=lambda x: x[0])
    WriteTsv(textsByDay, resultsPath / "TotalPostsByDay.tsv")

    textsByDayMax = sorted(textsByDay, key=lambda x: x[1], reverse=True)[:5]
    textsByDayMin = sorted(textsByDay, key=lambda x: x[1], reverse=False)[:5]
    agg = [["Max", ""]] + textsByDayMax + [["Min", ""]] + textsByDayMin

    WriteTsv(agg, resultsPath / "TotalPostsByDayAgg.tsv")

def CalcMessagesPerPerson(data):
    messageMap = {}
    for line in data:
        author = line[1]
        if author not in messageMap:
            messageMap[author] = 0
        messageMap[author] += 1
    messageList = [[k, v] for k, v in messageMap.items()]
    messageList = sorted(messageList, key=lambda x: x[1], reverse=True)
    return messageList

def ReadData(filepath):
    with open(filepath, "r", encoding="utf-8") as infile:
        data = infile.readlines()
    data = [x.replace("\n", "").split("\t") for x in data]
    data = [x for x in data if x is not None and len(x) > 0]
    return data

def Main():
    root = Path("C:/Users/brian/Documents/code/CarpetedBathroom")
    data = ReadData(root / "FacebookData" / "output.tsv")
    resultsPath = root / "Results"
    likesMap = PreProcessLikesMap(data)

    CalcTotalPosts(resultsPath, data, likesMap)
    
    CalcMessagesPerPerson(data)
    CalcLikesGiven(likesMap)
    

if __name__ == "__main__":
    Main()