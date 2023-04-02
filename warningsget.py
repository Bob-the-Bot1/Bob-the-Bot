# this is settings.py
import sqlite3

conn = sqlite3.connect("warnings.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS warnings
                (server_id INTEGER, user_id INTEGER, warn_code TEXT, moderator_id INTEGER, reason TEXT)''')
conn.commit()



def get_warnings(server_id: int, user_id: int) -> list:
    # Retrieve all warnings for the specified user and server
    cursor.execute("SELECT * FROM warnings WHERE server_id = ? AND user_id = ? ORDER BY rowid ASC", 
                           (server_id, user_id))
    return cursor.fetchall()

def get_warning_by_code(server_id: int, warn_code: str) -> tuple:
    # Retrieve the warning with the specified warning code
    cursor.execute("SELECT * FROM warnings WHERE server_id = ? AND warn_code = ?", 
                           (server_id, warn_code))
    return cursor.fetchone()

