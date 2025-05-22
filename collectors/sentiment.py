import sqlite3

def fetch_sentiment():
    print("⚠️ Using fallback sentiment")

    # Simulated sentiment data (manual or test values)
    long_percent = 64.3
    short_percent = 35.7
    source = "manual_fallback"

    # Save to database
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sentiment_data 
        (timestamp, long_percent, short_percent, source) 
        VALUES (datetime('now'), ?, ?, ?)
    """, (long_percent, short_percent, source))

    conn.commit()
    conn.close()
    print(f"✅ Sentiment saved: Long {long_percent}% | Short {short_percent}%")
