# import json
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import cohere 
import os
import sqlite3
from PyPDF2 import PdfReader 
from db import connect_db, create_notes_table, create_flashcards_table, create_studyguide_table,create_quiz_table, create_users_table, add_flashcard, add_note, add_quiz, get_total_notes, get_notes_read, get_all_users, get_user_flashcards, get_saved_notes, get_user_notes, get_user_quiz, update_user_progress, login_user, display_flashcards, display_notes, display_quizzes, display_users_table, get_study_guides, add_study_guide, mark_flashcard_as_reviewed, mark_notes_as_read
from auth import create_user_table, add_user, login_user
create_studyguide_table()
create_user_table()

st.set_page_config(
    page_title="Learning Assistant App"
)  

api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key)

if api_key is None:
    st.error("API key not found. Please set the COHERE_API_KEY environment variable.")
    st.stop()

# Ensure login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Login/Signup Page
def login_signup():
    st.title("Welcome to Study Buddy")

    if 'show_signup' not in st.session_state:
        st.session_state['show_signup'] = False

    # Toggle Login/Signup forms
    if st.session_state['show_signup']:
        st.header("Sign Up")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            add_user(username, password)
            st.success("Account created! Please log in.")
            st.session_state['show_signup'] = False
        if st.button("Back to Login"):
            st.session_state['show_signup'] = False

    else:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Incorrect username or password.")
        if st.button("Create an Account"):
            st.session_state['show_signup'] = True

if not st.session_state.get("logged_in", False):
    login_signup()
else:
    # Sidebar Navigation
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Dashboard", "Notes", "Summary", "Study Guide", "Flashcards", "Quiz"],
            icons=["house", "speedometer2", "book", "archive", "journal-bookmark", "card-text", "question-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # Home Page
    if selected == "Home":
        st.title("Home")
        st.text("Welcome to the Home page of your Study Buddy!")
        st.text("Use the sidebar to navigate through the app.")

    # Dashboard Section
    elif selected == "Dashboard":
        user_id = st.session_state.username
        total_notes = get_total_notes(user_id)
        notes_read = get_notes_read(user_id)
        progress = (notes_read / total_notes) * 100 if total_notes else 0

        st.title("User Progress Dashboard")
        st.write(f"Total Notes: {total_notes}")
        st.write(f"Notes Read: {notes_read}")
        st.progress(progress / 100)
        st.write(f"Progress: {progress:.2f}%")

        #   

    # Notes Section
    elif selected == "Notes":
        st.title("Notes")
        uploaded_file = st.file_uploader("Upload your notes (PDF or TXT)", type=["pdf", "txt"])
        user_id = st.session_state.username

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                notes = "".join([page.extract_text() for page in pdf_reader.pages])
            else:
                notes = uploaded_file.read().decode("utf-8")
            note_title = st.text_input("Enter the title for your notes", value="Untitled notes")

            if st.button("Save notes"):
                add_note(user_id, note_title, notes)
                st.success("Notes saved successfully")

        saved_notes = get_saved_notes(user_id)
        if saved_notes:
            note_titles = [note[0] for note in saved_notes]
            selected_note_title = st.selectbox("Choose your saved note to view", note_titles)
            selected_note = next(note for note in saved_notes if note[0] == selected_note_title)
            st.write(selected_note[1])
            mark_notes_as_read(selected_note[2])
            st.info(f"Note '{selected_note_title}' marked as read.")
        else:
            st.write("No saved notes available.")
            
    elif selected == "Summary":
        st.title("Summary")
        st.subheader("Welcome to the Summary page")
        st.text("Upload your notes below, or select previously saved notes to generate a summary.")
        
        # function to summarize notes using cohere API
        def summarize_notes(notes):
            response = co.generate(
                model='command-xlarge-nightly',
                prompt=f"summarize the following notes:\n\n{notes}\n\nSummarize the above content in a clear and concise way.",
                max_tokens=200,
            )
            summary = response.generations[0].text
            return summary

        

        # function to choose from saved notes(if available)
        user_id = 1
        saved_notes = get_saved_notes(user_id)
        if saved_notes:
            st.subheader("Choose from saved notes")
            selected_note = st.selectbox("Select saved notes to summarize", [note[0] for note in saved_notes])
            if selected_note:
                # get selected notes' content
                note_content = next(note[1] for note in saved_notes if note[0] == selected_note)
                if st.button("Summarize selected notes"):
                    with st.spinner("Summarizing..."):
                        summary = summarize_notes(note_content)
                        st.subheader("Summary:")
                        st.write(summary)

        st.subheader("Upload New Notes")
        uploaded_file = st.file_uploader("Upload your notes (PDF or TXT)", type=["pdf", "txt"])

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                pdf_reader = PdfReader(uploaded_file)
                notes = ""
                for page in pdf_reader.pages:
                    notes += page.extract_text()
            else:
                notes = uploaded_file.read().decode("utf-8")

            st.write("Here is a preview of your uploaded notes:")
            st.write(notes[:200] + "...")

            # generate summary button
            if st.button("Summarize uploaded notes"):
                with st.spinner("Summarizing..."):
                    summary = summarize_notes(notes)
                    st.subheader("Summary")
                    st.write(summary)

    # Flashcards Section
    elif selected == "Flashcards":
        st.title("Generate and View Flashcards")

        def generate_flashcards(notes):
            response = co.generate(
                model='command-xlarge-nightly',
                prompt=f"Generate 5 flashcards with questions and answers:\n\n{notes}",
                max_tokens=200,
            )
            flashcards_text = response.generations[0].text
            flashcards = []
            lines = flashcards_text.split("\n")
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    question = lines[i].strip()
                    answer = lines[i + 1].strip()
                    flashcards.append(({"question": question, "answer": answer}))
            return flashcards

        user_id = st.session_state.username
        saved_notes = get_saved_notes(user_id)
        if saved_notes:
            note_titles = [note[0] for note in saved_notes]
            selected_note = st.selectbox("Choose your notes", note_titles)
            note_content = next(note[1] for note in saved_notes if note[0] == selected_note)

            if st.button("Generate Flashcards"):
                flashcards = generate_flashcards(note_content)
                for flashcard in flashcards:
                    add_flashcard(user_id, flashcard["question"], flashcard["answer"])
                st.success("Flashcards generated and saved successfully!")

        flashcards = get_user_flashcards(user_id)
        if flashcards:
            st.subheader("Your Flashcards")
            for i, flashcard in enumerate(flashcards):
                question = flashcard[1]
                answer = flashcard[2]
                flip_state = f"flip_{i}"
                if flip_state not in st.session_state:
                    st.session_state[flip_state] = False

                if st.session_state[flip_state]:
                    st.write(f"Answer: {answer}")
                    if st.button(f"Show Question {i}"):
                        st.session_state[flip_state] = False
                else:
                    st.write(f"Question: {question}")
                    if st.button(f"Show Answer {i}"):
                        st.session_state[flip_state] = True
        else:
            st.write("No flashcards available.")
    elif selected == "Quiz":
        st.title("Quiz")
        st.text("Welcome to the Quiz page")
        st.text("This is where you can generate quizzes from your notes")
        st.text("You can also view and edit your quizzes here")
        st.write("Click here to generate a quiz")
        
        # function to generate quiz
        def generate_quiz(notes):
            response = co.generate(
            model='command-xlarge-nightly',
            prompt=f"generate a 10 question quiz with choices to choose from from the following notes:\n\n{notes}",
            max_tokens=200,
        )
            quiz = response.generations[0].text
            return quiz


        # Retrieve saved notes
        user_id = 1  # Example user_id
        saved_notes = get_saved_notes(user_id)

        # If there are saved notes, let the user select one
        if saved_notes:
            note_titles = [note[0] for note in saved_notes]  # Get note titles
            selected_note = st.selectbox("Choose your notes", note_titles)

            # Get the content of the selected note
            note_content = next(note[1] for note in saved_notes if note[0] == selected_note)

            st.write(f"Selected Notes: {selected_note}")
            st.write(note_content[:500] + "...")  # Show preview of the notes

            # Generate quiz based on the selected notes
            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz = generate_quiz(note_content)
                    st.write(quiz)
        else:
            st.write("No saved notes available.")



    # Study Guide Page Logic
    elif selected == "Study Guide":
        st.title("Generate Your Study Guide")
        
        # Function to generate a study guide from notes
        def generate_study_guide(notes):
            response = co.generate(
            model='command-xlarge-nightly',
            prompt=f"Generate a study guide based on these notes:\n\n{notes}\n\nThe study guide should summarize key points and suggest topics to focus on.",
            max_tokens=300
        )
            study_guide = response.generations[0].text
            return study_guide

        user_id = 1 

        # Fetch saved notes from the database
        saved_notes = get_saved_notes(user_id)
        
        if saved_notes:
            # Let the user select a note from a dropdown
            note_titles = [note[0] for note in saved_notes]  # Get titles of saved notes
            selected_note_title = st.selectbox("Choose your notes", note_titles)

            # Retrieve the content of the selected note
            note_content = next(note[1] for note in saved_notes if note[0] == selected_note_title)

            st.write(f"Selected Notes: {selected_note_title}")
            st.write(note_content[:500] + "...")  # Show a preview of the selected notes

            # Generate Study Guide
            if st.button("Generate Study Guide"):
                with st.spinner("Generating your study guide..."):
                    study_guide = generate_study_guide(note_content)
                    st.subheader("Generated Study Guide")
                    st.write(study_guide)

                    # Save the generated study guide to the database
                    add_study_guide(user_id, study_guide)
                    st.success("Study guide saved successfully!")

        else:
            st.write("No saved notes available. Please upload notes on the Notes page.")

        # Display saved study guides
        st.subheader("Your Saved Study Guides")
        saved_guides = get_study_guides(user_id)

        if saved_guides:
            for guide in saved_guides:
                st.write(f"Study Guide:\n\n{guide[0]}")
        else:
            st.write("No study guides available.")   
             
# Footer Disclaimer (using markdown and HTML)
footer = """
    <style>
        .footer {
            background-color: #181818;
            color: #f0f2f6;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            z-index: 1000;
        }
    </style>
    <div class="footer">
        <p><small>Disclaimer: AI-generated content may contain inaccuracies. Please verify critical information from trusted sources.</small></p>
    </div>
"""

# Display the footer on every page
st.markdown(footer, unsafe_allow_html=True)