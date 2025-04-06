import sqlite3
conn = sqlite3.connect('database/candidates.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM candidates")
conn.commit()
conn.close()
print("Database reset successfully.")
