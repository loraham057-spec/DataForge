import sqlite3

db = r"data\database\data_collection.db"

conn = sqlite3.connect(db)

print("TABLES :")

tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

print(tables)

conn.close()
