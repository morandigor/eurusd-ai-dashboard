import pandas as pd
import sqlite3
import os

def fetch_cot():
    print("🔄 Running fetch_cot (CSV version)")

    file_path = os.path.join("data", "deacmelf.csv")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    # Filter Euro FX rows (pre-filtered CSV from me)
    if df.empty:
        print("❌ No rows found in CSV.")
        return

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    added = 0
    for _, row in df.iterrows():
        try:
            report_date = pd.to_datetime(row['Report Date']).strftime("%Y-%m-%d")
            non_comm_long = int(str(row['Noncommercial Long']).replace(',', '').strip())
            non_comm_short = int(str(row['Noncommercial Short']).replace(',', '').strip())

            cursor.execute("""
                INSERT OR IGNORE INTO cot_reports 
                (report_date, non_commercial_long, non_commercial_short) 
                VALUES (?, ?, ?)
            """, (
                report_date,
                non_comm_long,
                non_comm_short
            ))
            added += 1
        except Exception as err:
            print(f"⚠️ Skipped row due to error: {err}")
            continue

    conn.commit()
    conn.close()
    print(f"✅ COT data added for {added} rows.")
