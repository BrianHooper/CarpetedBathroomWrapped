from pathlib import Path
import os
from datetime import datetime
import json

def WriteTsv(data, filepath):
    data = ["\t".join([str(y) for y in x]) + "\n" for x in data]
    with open(filepath, "w", encoding="utf-8") as outfile:
        outfile.writelines(data)

def find_first_ascii_index(string):
  for i, char in enumerate(string):
    if ord(char) < 128:
      return i
  return -1  # Return -1 if no ASCII character is found

def extractReaction(likeStr):
    emojiEndIdx = find_first_ascii_index(likeStr)
    emoji = likeStr[:emojiEndIdx]
    parenthesisIdx = likeStr.index(" (")
    author = likeStr[emojiEndIdx:parenthesisIdx]
    timestamp = likeStr[parenthesisIdx+2:-1]
    return emoji, author, timestamp



def CalcLikesGiven(resultsPath, likesMap):
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
            emoji, author, timestamp = extractReaction(likeStr)
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

def CalcMessagesPerPerson(resultsPath, data):
    messageMap = {}
    for line in data:
        author = line[1]
        if author not in messageMap:
            messageMap[author] = 0
        messageMap[author] += 1
    messageList = [[k, v] for k, v in messageMap.items()]
    messageList = sorted(messageList, key=lambda x: x[1], reverse=True)    
    WriteTsv(messageList, resultsPath / "TotalMessagesPerPerson.tsv")

def ReadData(filepath):
    with open(filepath, "r", encoding="utf-8") as infile:
        data = infile.readlines()
    data = [x.replace("\n", "").split("\t") for x in data]
    data = [x for x in data if x is not None and len(x) > 0]
    return data

def CalcMostLikedPosts(resultsPath, data):
    likedPosts = [x for x in data if len(x[4]) > 0 and len(x[2]) > 0]
    likedPosts = sorted(likedPosts, key=lambda x: len(x[4].split("%%")), reverse=True)[:10]
    WriteTsv(likedPosts, resultsPath / "MostLikedPosts.tsv")

def CalcEmojiTotals(resultsPath, data, likesMap):
    emojiCountMap = {}
    
    for person, emojiMap in likesMap.items():
        for emoji, messages in emojiMap.items():
            if emoji not in emojiCountMap:
                emojiCountMap[emoji] = 0
            emojiCountMap[emoji] += len(messages)
    emojiList = [[k, v] for k, v in emojiCountMap.items()]
    emojiList = sorted(emojiList, key=lambda x: x[1], reverse=True)
    WriteTsv(emojiList, resultsPath / "EmojiList.tsv")

def CalculatePersonTotals(resultsPath, data, likesMap):
    authors = set([x[1] for x in data])
    for author in authors:
        pass
        totalPosts = len([x for x in data if x[1] == author and len(x[2]) > 0])
        totalMedia = len([x for x in data if x[1] == author and len(x[3]) > 0])
        totalLikes = sum(len(v) for v in likesMap[author].values())
        likedPostsMap = {}
        for messageList in likesMap[author].values():
            for message in messageList:
                if message[1] not in likedPostsMap:
                    likedPostsMap[message[1]] = 0
                likedPostsMap[message[1]] += 1
        mostLikedOtherPeople = sorted([[k, v] for k, v in likedPostsMap.items()], key=lambda x: x[1], reverse=True)[:3]
        
        mostLikedByMap = {}
        for emojiMap in likesMap.values():
            for messageList in emojiMap.values():
                for message in messageList:
                    messageAuthor = message[1]
                    if messageAuthor != author:
                        continue
                    for likeStr in message[4].split("%%"):
                        emoji, likeAuthor, timestamp = extractReaction(likeStr)
                        if likeAuthor not in mostLikedByMap:
                            mostLikedByMap[likeAuthor] = 0
                        mostLikedByMap[likeAuthor] += 1
        mostLikedBy = sorted([[k, v] for k, v in mostLikedByMap.items()], key=lambda x: x[1], reverse=True)[:3]
        
        textsByDayMap = {}
        for line in [x for x in data if x[1] == author]:
            if len(line[2]) == 0:
                continue
            dt = datetime.strptime(line[0], "%b %d, %Y %I:%M:%S %p")
            date = dt.strftime("%Y-%m-%d")
            if date not in textsByDayMap:
                textsByDayMap[date] = 0
            textsByDayMap[date] += 1
        textsByDay = sorted([[k, v] for k, v in textsByDayMap.items()], key=lambda x: x[0])
        authorData = {
            "name": author,
            "totalPosts": totalPosts,
            "totalMedia": totalMedia,
            "totalReactions": totalLikes,
            "mostLiked": mostLikedOtherPeople,
            "mostLikedBy": mostLikedBy,
            "textsByDay": textsByDay
        }
        with open(resultsPath / "people" / f"{author}.json".replace(" ", ""), "w", encoding="utf-8") as outfile:
            json.dump(authorData, outfile)

def Main():
    root = Path("C:/Users/brian/Documents/code/CarpetedBathroom")
    data = ReadData(root / "FacebookData" / "output.tsv")
    resultsPath = root / "Results"
    likesMap = PreProcessLikesMap(data)

    # CalcTotalPosts(resultsPath, data, likesMap)
    # CalcMessagesPerPerson(resultsPath, data)
    # CalcLikesGiven(resultsPath, likesMap)
    # CalcMostLikedPosts(resultsPath, data)
    # CalcEmojiTotals(resultsPath, data, likesMap)
    CalculatePersonTotals(resultsPath, data, likesMap)


if __name__ == "__main__":
    Main()