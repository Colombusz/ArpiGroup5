import sqlite3

# Database file path
db_path = 'Arpi.sql'

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# SQL statement to create a table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfid TEXT NOT NULL UNIQUE,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# Execute the SQL statement
cursor.execute(create_table_sql)

# Commit changes and close connection
conn.commit()
conn.close()

print("Table 'users' created successfully.")