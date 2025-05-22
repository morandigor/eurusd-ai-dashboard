import sqlite3
import os

def create_tables():
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/database.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS eurusd_prices (
            timestamp TEXT PRIMARY KEY,
            open REAL, high REAL, low REAL, close REAL, volume REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS economic_events (
            timestamp TEXT, event TEXT, country TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS cot_reports (
            report_date TEXT PRIMARY KEY,
            non_commercial_long INT,
            non_commercial_short INT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_data (
            timestamp TEXT, long_percent REAL, short_percent REAL, source TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS news_headlines (
            timestamp TEXT, source TEXT, title TEXT
        )
    ''')

    conn.commit()
    conn.close()
