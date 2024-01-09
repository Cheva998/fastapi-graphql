import sqlite3

# Establish a connection to the database
conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# Create a table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
    """
)

# Insert sample data
data = [
    ("test", "first testing item")
]

cursor.executemany("INSERT INTO items (name, description) VALUES (?, ?)", data)

conn.commit()
conn.close()

print('creation complete')