# -*- coding: utf-8 -*-
"""外网新闻抓取（跑在 GitHub Actions 海外服务器，绕过国内墙）。

按关键词抓 Google News RSS → 过滤去重 → 输出 JSON 到 stdout。
GitHub Action 会把 stdout 重定向保存为 news.json 并 commit 回仓库。
"""
import datetime
import hashlib
import json
import urllib.parse

import feedparser

# A 股相关的海外事件关键词（可自行增删）
KEYWORDS = [
    "Nvidia", "semiconductor", "chip export control", "Federal Reserve rate",
    "TSMC", "ASML", "data center capex", "AI chip", "China EV battery",
    "oil price", "copper price", "lithium", "US China tariff", "sanctions China",
    "robot", "innovative drug FDA", "solid state battery",
]


def fetch(query):
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(query)
           + "&hl=en-US&gl=US&ceid=US:en")
    feed = feedparser.parse(url)
    out = []
    for e in feed.entries:
        title = (e.get("title") or "").split(" - ")[0].strip()
        if not title:
            continue
        out.append({
            "title": title,
            "source": e.get("source", {}).get("title", ""),
            "link": e.get("link", ""),
            "published": e.get("published", ""),
        })
    return out


def main():
    items, seen = [], set()
    for q in KEYWORDS:
        try:
            for it in fetch(q):
                h = hashlib.md5(it["title"].encode("utf-8")).hexdigest()
                if h in seen:
                    continue
                seen.add(h)
                items.append({"query": q, **it})
        except Exception as e:
            print(f"  [warn] {q}: {e}", file=__import__("sys").stderr)

    print(json.dumps({
        "fetched_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "count": len(items),
        "items": items,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
