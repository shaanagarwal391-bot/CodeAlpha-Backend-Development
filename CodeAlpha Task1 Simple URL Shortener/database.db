import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM urls")
    rows = cursor.fetchall()
    
    print("\n--- SAVED URL MAPPINGS ---")
    print(f"{'ID':<5} | {'Short Code':<12} | {'Original Long URL'}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<5} | {row[2]:<12} | {row[1]}")
except sqlite3.OperationalError:
    print("The database or table doesn't exist yet. Run app.py first!")

conn.close()
