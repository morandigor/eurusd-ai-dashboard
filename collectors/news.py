import feedparser
import sqlite3

def fetch_news():
    print("Fetching news headlines...")
    url = "https://finance.yahoo.com/rss/forex"
    feed = feedparser.parse(url)

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    for item in feed.entries[:10]:
        cursor.execute("""
            INSERT INTO news_headlines 
            (timestamp, source, title) 
            VALUES (?, ?, ?)
        """, (
            item.published,
            "Yahoo Finance",
            item.title
        ))

    conn.commit()
    conn.close()
