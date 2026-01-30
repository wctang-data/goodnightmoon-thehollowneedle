# /// script
# dependencies = [
#   "pydub",
#   "python-dotenv",
# ]
# ///

from pprint import pprint
import os
import datetime
import re
import glob
from xml.etree import ElementTree
import pydub
from dotenv import load_dotenv

RFC822 = "%a, %d %b %Y %H:%M:%S %z"


def main():
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'), override=True)

    name = os.getenv("PODCAST_NAME")
    repo = os.getenv('REPO_NAME')
    print(name, repo)
    if not name or not repo:
        print(f"!!! PODCAST_NAME not defined!!")
        return

    items = {}
    # old_items = {}
    if os.path.exists("feed.xml"):
        with open("feed.xml", "r", encoding="utf-8") as f:
            xx = ElementTree.fromstring(f.read())
            for item in xx.findall(".//item"):
                url = item.find("enclosure").get("url")
                filename = url[url.rfind("/")+1:]
                title = item.find("title").text
                length = item.find("enclosure").get("length")
                duration = item.find("{*}duration").text
                pubdate = item.find("pubDate").text

                items[filename] = [title, length, duration, pubdate, False]

    rex = re.compile(r'^(.*)\.(mp3|m4a)$')
    # for dirpath, _, filenames in os.walk("."):
    for filename in glob.glob("*.m*"):
        if not (m := rex.match(filename)):
            continue

        if filename not in items:
            info = pydub.utils.mediainfo(filename)
            items[filename] = [m[1], info["size"], info["duration"], None, True]
            print(f'{filename}: {info["duration"]}')
        else:
            items[filename][4] = True

    for filename in items:
        if not items[filename][4]:
            print(f"!!! {filename} in feed.xml but not in filesystem.")
            return

    rex = re.compile(r'^\d+_(.*)\.(mp3|m4a)$')
    _day_s = datetime.datetime(2025, 1, 1)
    _now = datetime.datetime.now().astimezone()
    idx = 0
    for filename, vv in items.items():
        if vv[3] is None:
            if m := rex.match(filename):
                vv[3] = datetime.datetime.strptime(filename[:8], "%Y%m%d").replace(tzinfo=_now.tzinfo).strftime(RFC822)
            else:
                # vv[3] = (_now - datetime.timedelta(days=len(items)-int(filename[:2]))).strftime(RFC822)
                vv[3] = (_day_s + datetime.timedelta(days=idx)).strftime(RFC822)
        idx += 1



    with open("feed.xml", "w", encoding="utf-8", newline='\n') as out:
        print(f'<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0"><channel><title>{name}</title><description>{name}</description><itunes:image href="https://wctang-data.github.io/{repo}/logo.png"/><link>https://wctang-data.github.io/{repo}/</link><language/><pubDate>{_now.strftime(RFC822)}</pubDate><author>wctang-data</author>', file=out)
        for filename, vv in sorted(items.items()):
            mm = 'mp4' if os.path.splitext(filename)[1] == '.m4a' else 'mpeg'
            print(f'<item><title>{vv[0]}</title><pubDate>{vv[3]}</pubDate><enclosure url="https://wctang-data.github.io/{repo}/{filename}" type="audio/{mm}" length="{vv[1]}"/><itunes:duration>{int(float(vv[2]))}</itunes:duration></item>', file=out)
        print('</channel></rss>', file=out)

    with open("index.html", "w", encoding="utf-8", newline='\n') as out:
        print(f'<!DOCTYPE html><html><head><title>{name}</title></head><body><h1>{name}</h1><p><img src="https://wctang-data.github.io/{repo}/logo.png" /></p><a href="https://wctang-data.github.io/{repo}/feed.xml">feed</a><ul>', file=out)
        for filename, vv in sorted(items.items()):
            print(f'<li><a href="https://wctang-data.github.io/{repo}/{filename}">{vv[0]}</a></li>', file=out)
        print(f'</ul></body><p>{_now}</p></html>', file=out)


if __name__ == '__main__':
    main()
