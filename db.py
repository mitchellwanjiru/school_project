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
            username TEXT UNIQUE NOT NULL,
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
    
#function to add data into users table
def add_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
#function to get data from users table
def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
#function to add data to flashcards table
def add_flashcard(user_id, question, answer):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO flashcards (user_id, question, answer) VALUES (?, ?)', (user_id, question, answer))
    conn.commit()
    conn.close()
#function to add data to quiz table
def add_quiz(user_id, quiz_data, score):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO quiz (user_id, quiz_data, score) VALUES(?, ?)' (user_id, quiz_data, score))
    conn.commit()
    conn.close()
#function to add data to notes table
def add_note(user_id, note_title, note_content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (user_id, note_title, note_content) VALUES(?, ?)' (user_id, note_title, note_content))
    conn.commit()
    conn.close()

#function to retrieve data from users table
def get_all_users():
    conn =  connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users
#function to retrieve data from flashcards table
def get_user_flashcards(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flashcards WHERE user_id = ?', (user_id))
    flashcards = cursor.fetchall()
    conn.close()
    return flashcards
#function to retrieve data from quiz table
def get_user_quiz(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quiz WHERE user_id = ?', (user_id))
    quiz = cursor.fetchall()
    conn.close()
    return quiz
#function to retrieve data from notes table
def get_user_notes(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes WHERE user_id = ?', (user_id))
    notes = cursor.fetchall()
    conn.close()
    return notes

#function to update user progress
def update_user_progress(user_id, new_progress):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET progress = ? WHERE id = ?', (new_progress, user_id))
    conn.commit()
    conn.close()

#function to display quizzes, flashcards, notes, users tables repectively
def display_quizzes(user_id):
    quizzes = get_user_quiz(user_id)
    return quizzes

def display_flashcards(user_id):
    flashcards = get_user_flashcards(user_id)
    return flashcards

def display_notes(user_id):
    notes = get_user_notes(user_id)
    return notes

def display_users_table():
    users = get_all_users()
    return users
