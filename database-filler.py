import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor(
