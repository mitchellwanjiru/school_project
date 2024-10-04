import sqlite3

# Function to connect to the database
def connect_db():
    return sqlite3.connect('learning_assistant.db')

# Function to create the notes table if it doesn't exist
def create_notes_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            note_title TEXT NOT NULL,
            note_content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()
