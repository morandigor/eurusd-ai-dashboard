import feedparser
import sqlite3

def fetch_events():
    print("Fetching economic events...")
    url = 'https://www.forexfactory.com/ff_calendar_thisweek.xml'
    feed = feedparser.parse(url)

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    for entry in feed.entries:
        cursor.execute("""
            INSERT INTO economic_events 
            (timestamp, event, country) 
            VALUES (?, ?, ?)
        """, (
            entry.published,
            entry.title,
            "EUR/USD"
        ))

    conn.commit()
    conn.close()
