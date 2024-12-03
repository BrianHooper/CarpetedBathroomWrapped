from bs4 import BeautifulSoup
import os
from pathlib import Path

class Message:
    def __init__(self, timestamp, author, text, media, likes):
        self.timestamp = timestamp
        self.author = author
        self.text = text
        self.media = media
        self.likes = likes
    
    def __str__(self):
        cols = []
        for col in [self.timestamp, self.author, self.text, self.media, "%%".join(self.likes)]:
            if col is not None and len(col) > 0:
                cols.append(col)
            else:
                cols.append("")

        return "\t".join(cols) + "\n"

def ExtractMedia(element: BeautifulSoup):
    div = element.find("div", { "class": "_2ph_ _a6-p" })
    if div is None:
        return None
    img = div.find("img")
    if img is not None:
        return img.attrs["src"]
    video = div.find("video")
    if video is not None:
        return video.attrs["src"]
    audio = div.find("audio")
    if audio is not None:
        return audio.attrs["src"]
    return None
    
def ExtractMessage(element: BeautifulSoup):
    div = element.find("div", { "class": "_2ph_ _a6-p" })
    if div is None:
        return None
    div = div.find("div")
    if div is None:
        return None
    children = div.find_all("div")
    if children is None or len(children) < 2:
        return None
    text = children[1].text
    if text is None or len(text) == 0:
        return None
    return text

def ExtractLikes(element: BeautifulSoup) -> list:
    ul = element.find("ul", { "class": "_a6-q" })
    if ul is None:
        return []
    lis = ul.find_all("li")
    if lis is None or len(lis) == 0:
        return []
    likes = []
    for li in lis:
        like = li.text
        likes.append(like)
    return likes

def Extract(element: BeautifulSoup, className: str) -> str | None:
    div = element.find("div", { "class": className })
    if div is None:
        return None
    text = div.text
    if text is None or len(text) == 0:
        return None
    return text

def ProcessMessage(element: BeautifulSoup):
    author = Extract(element, "_2ph_ _a6-h _a6-i")
    if author is None:
        return None
    
    message = ExtractMessage(element)
    media = ExtractMedia(element)
    if message is None and media is None:
        return None
    
    likes = ExtractLikes(element)
    
    timestamp = Extract(element, "_3-94 _a6-o")
    if timestamp is None:
        return None

    return Message(timestamp, author, message, media, likes)

def ReadFile(filepath: Path) -> BeautifulSoup:
    with open(filepath, "r", encoding="utf-8") as infile:
        data = infile.read()
    soup = BeautifulSoup(data, "html.parser")
    return soup

def ProcessFile(filepath: Path):
    soup = ReadFile(filepath)
    messageElements = soup.find_all("div", {"class": "_a6-g"})
    count = 0
    messages = []
    for element in messageElements:
        message = ProcessMessage(element)
        if message is not None:
            messages.append(message)
        else:
            count += 1
    print(f"Skipped {count}")
    return messages

def Main():
    root = Path("C:/Users/brian/Documents/code/CarpetedBathroom")
    dataFolder = root / "FacebookData"
    htmlFilepaths = [y for y in [dataFolder / x for x in os.listdir(dataFolder)] if y.suffix == ".html"]
    messages = []
    for htmlFilepath in htmlFilepaths:
        messages += ProcessFile(htmlFilepath)
    with open(root / "output.tsv", "w", encoding="utf-8") as outfile:
        outfile.writelines([str(m) for m in messages])

if __name__ == "__main__":
    Main()