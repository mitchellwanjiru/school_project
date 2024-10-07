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
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# function to create the users table
def create_users_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
            progress INTEGER DEFAULT 0
        )           
       ''')
    conn.commit()
    conn.close()
    
#function to create flashcards table
def create_flashcards_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
            )           
            '''   )
    conn.commit()
    conn.close()
    
#function to create quiz table
def create_quiz_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(''' 
          CREATE TABLE IF NOT EXISTS quiz(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              quiz_data TEXT NOT NULL,
              score INTEGER DEFAULT 0,
              FOREIGN KEY (user_id) REFERENCES users(user_id)
          )            
            ''')
    conn.commit()
    conn.close()