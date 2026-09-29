#!/usr/bin/env python3
import html, re
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://thekenziereport.co.uk"
SECTIONS = ["Latest","Politics","Reform","Britain","Westminster","Economy","NHS","Immigration","Opinion","Analysis"]

def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return {}, text
    data = {}
    current = None
    for line in m.group(1).splitlines():
        if re.match(r"^\w+\s*:", line):
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip("'\"")
            current = k.strip()
        elif current and line.startswith("  "):
            data[current] = (data.get(current, "") + " " + line.strip()).strip()
    return data, m.group(2).strip()

articles=[]
for path in sorted(Path("articles").glob("*.md")):
    data, body = parse(path)
    if str(data.get("published","true")).lower() in {"false","no","0"}:
        continue
    title=data.get("title", path.stem)
    date=data.get("date","")
    excerpt=data.get("excerpt") or data.get("standfirst") or re.sub(r"[*_#>\[\]]","",body).replace("\n"," ")
    articles.append({"slug":path.stem,"title":title,"date":date,"excerpt":excerpt[:220]})

urls=[f"{BASE}/"]+[f"{BASE}/?section={s}" for s in SECTIONS]+[f"{BASE}/articles/{a['slug']}.html" for a in articles]
now=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
sitemap=["<?xml version=\"1.0\" encoding=\"UTF-8\"?>","<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
for u in urls:
    sitemap += [f"  <url><loc>{html.escape(u, quote=True)}</loc></url>"]
sitemap += ["</urlset>"]
Path("sitemap.xml").write_text("\n".join(sitemap)+"\n",encoding="utf-8")

rss=["<?xml version=\"1.0\" encoding=\"UTF-8\"?>","<rss version=\"2.0\"><channel>",
"<title>The Kenzie Report</title>",f"<link>{BASE}/</link>","<description>Politics. Britain. Unfiltered.</description>",
f"<lastBuildDate>{now}</lastBuildDate>"]
for a in sorted(articles,key=lambda x:x["date"],reverse=True)[:50]:
    link=f"{BASE}/articles/{a['slug']}.html"
    rss += [f"<item><title>{html.escape(a['title'])}</title><link>{html.escape(link)}</link><guid isPermaLink=\"true\">{html.escape(link)}</guid><description>{html.escape(a['excerpt'])}</description><pubDate>{html.escape(a['date'])}</pubDate></item>"]
rss += ["</channel></rss>"]
Path("rss.xml").write_text("\n".join(rss)+"\n",encoding="utf-8")
