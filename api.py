from fastapi import FastAPI
import feedparser, urllib.parse

app = FastAPI()

@app.get("/api/rss")
def get_rss(keyword: str = "bts", limit: int = 10):
    q = urllib.parse.quote(f'"{keyword}"')
    rss_url = f"https://www.reddit.com/search.rss?q={q}&sort=new"

    feed = feedparser.parse(rss_url)

    items = []
    for entry in feed.entries[:limit]:
        items.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.get("published", "")
        })

    return {"keyword": keyword, "count": len(items), "items": items}
