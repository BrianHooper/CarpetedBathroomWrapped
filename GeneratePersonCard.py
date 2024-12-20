import json
from pathlib import Path
import os
from datetime import datetime

template = """

            <div class="blue" id="%%AUTHOR%%">
                <div class="card">

                    <div class="posttitle">
                        <div class="posticon"><img class="authoricon" src="Icons/%%AUTHOR%%.png" /></div>
                        <div class="postauthor">%%NAME%%</div>
                    </div>

                    <div class="row">
                        <div class="col">
                            <div>Total texts: %%TEXTS%%</div>
                            <div>Total media: %%MEDIA%%</div>
                            <div>Total reactions given: %%REACTIONSGIVEN%%</div>
                            <div>Total reactions recieved: %%REACTIONSRECIEVED%%</div>
                            <div>Days active: %%DAYSACTIVE%%</div>
                            <div>Most active day: %%MOSTACTIVEDAY%%</div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col">
                            <div>Most reactions given:</div>
%%MOSTLIKED%%
                        </div>
                        <div class="col">
                            <div>Most reactions recieved:</div>
%%MOSTLIKEDBY%%
                        </div>
                    </div>
                </div>
            </div>
"""

def GenerateHtml(author, data):
    html = template
    html = html.replace("%%AUTHOR%%", author)
    html = html.replace("%%NAME%%", data["name"])
    html = html.replace("%%TEXTS%%", str(data["totalPosts"]))
    html = html.replace("%%MEDIA%%", str(data["totalMedia"]))
    html = html.replace("%%REACTIONSGIVEN%%", str(data["totalReactionsGiven"]))
    html = html.replace("%%REACTIONSRECIEVED%%", str(data["totalReactionsRecieved"]))

    html = html.replace("%%MOSTLIKED%%", "\n".join([f"                            <div>{x[0]}: {x[1]}</div>" for x in data["mostLiked"]]))
    html = html.replace("%%MOSTLIKEDBY%%", "\n".join([f"                            <div>{x[0]}: {x[1]}</div>" for x in data["mostLikedBy"]]))
    html = html.replace("%%DAYSACTIVE%%", str(len(data["textsByDay"])))
    mostActiveDay = sorted(data["textsByDay"], key=lambda x: x[1], reverse=True)[0]
    mostActiveDayStr = datetime.strptime(mostActiveDay[0], "%Y-%m-%d").strftime("%b %d, %Y")
    html = html.replace("%%MOSTACTIVEDAY%%", f"{mostActiveDayStr} ({mostActiveDay[1]})")

    return html

def Main():
    root = Path("C:/Users/brian/Documents/code/CarpetedBathroom/Results/People")
    htmls = []
    for filename in os.listdir(root):
        filepath = root / filename
        if filepath.suffix != ".json":
            continue
        author = filepath.stem
        with open(filepath, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        html = GenerateHtml(author, data)
        htmls.append([html, data["totalPosts"]])
    htmls = sorted(htmls, key=lambda x: x[1], reverse=True)
    htmls = "\n\n".join([x[0] for x in htmls])
    with open(root / f"people.html", "w", encoding="utf-8") as outfile:
        outfile.write(htmls)


if __name__ == "__main__":
    Main()