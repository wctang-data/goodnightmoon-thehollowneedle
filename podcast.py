#!/usr/bin/env python3

import os
import datetime
import pydub
import re

def main():
    base = "https://wctang-data.github.io/goodnightmoon-thehollowneedle"
    name = "晚安．月亮 - 亞森羅蘋 - 奇巖城"
    rex = re.compile(r'.*_(.*)\.mp3')

    items = []
    for dirpath, _, filenames in os.walk("."):
        dirpath = dirpath[2:]
        if dirpath.startswith(".git"):
            continue
        for filename in filenames:
            if not (m := rex.match(filename)):
                continue
            info = pydub.utils.mediainfo(f'{filename}')
            items.append((f'{m[1]}', filename, info["size"], info["duration"]))

    RFC822 = "%a, %d %b %Y %H:%M:%S %z"
    _now = datetime.datetime.now().astimezone()
    with open("feed.xml", "w", encoding="utf-8", newline='\n') as out:
        print(f'<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0"><channel><title>{name}</title><description>{name}</description><itunes:image href="{base}/logo.png"/><link>{base}/</link><language/><pubDate>{_now.strftime(RFC822)}</pubDate><author>wctang-data</author>', file=out)
        for idx, item in enumerate(items):
            print(f'<item><title>{item[0]}</title><pubDate>{(_now+datetime.timedelta(days=-len(items)+idx)).strftime(RFC822)}</pubDate><enclosure url="{base}/{item[1]}" type="audio/mpeg" length="{item[2]}"/><itunes:duration>{int(float(item[3]))}</itunes:duration></item>', file=out)
        print('</channel></rss>', file=out)

    with open("index.html", "w", encoding="utf-8", newline='\n') as out:
        print(f'<!DOCTYPE html><html><head><title>{name}</title></head><body><h1>{name}</h1><p><img src="{base}/logo.png" /></p><a href="{base}/feed.xml">feed</a><ul>', file=out)
        for idx, item in enumerate(items):
            print(f'<li><a href="{base}/{item[1]}">{item[0]}</a></li>', file=out)
        print(f'</ul></body><p>{_now}</p></html>', file=out)


if __name__ == '__main__':
    main()
