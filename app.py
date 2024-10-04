# import json
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import cohere 
import os
import sqlite3
from PyPDF2 import PdfReader 
from db import connect_db, create_notes_table
create_notes_table()
# from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Learning Assistant App"
)  

api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(api_key)

if api_key is None:
    st.error("API key not found. Please set the COHERE_API_KEY environment variable.")
    st.stop()



with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Dashboard", "Notes", "Summary", "Study Guide", "Flashcards", "Quiz"],
        icons=["house", "speedometer2", "book", "archive", "journal-bookmark", "card-text", "question-circle"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Home":
    st.title("Home")
    st.text("Welcome to the Home page")
    st.text("This is where you can find an overview of your progress and access other features of the app")
    st.text("Use the sidebar to navigate to other pages")
    st.text("Enjoy using the Learning Assistant App!")
    
elif selected == "Dashboard":
    total_notes = 100
    notes_read = 75

# Calculate progress percentage
    progress = (notes_read / total_notes) * 100

# Streamlit dashboard
    st.title("User Progress Dashboard")
    st.write(f"Total Notes: {total_notes}")
    st.write(f"Notes Read: {notes_read}")
    st.progress(progress / 100)
    st.write(f"Progress: {progress:.2f}%")
    st.write("Keep up the good work!")

elif selected == "Notes":
    st.title("Notes")
    st.text("Welcome to the Notes page")
    st.text("This is where you can upload your notes")
    st.text("You can also view and edit your notes here")
    st.write("Click here to upload your notes")
    st.button("Upload Notes")
    
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

    # Function to retrieve saved notes from the database
    def get_saved_notes():
        conn = sqlite3.connect('learning_assistant.db')
        cursor = conn.cursor()
        cursor.execute('SELECT note_title, note_content FROM notes')
        notes = cursor.fetchall()
        conn.close()
        return notes

    # function to choose from saved notes(if available)
    saved_notes = get_saved_notes()
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
      
    

elif selected == "Study Guide":
    st.title("Study Guide")
    st.text("Welcome to the Study Guide page")
    st.text("This is where you can generate study guides from your notes")
    st.text("You can also view and edit your study guides here")
    st.write("Click here to generate a study guide")
    st.button("Generate Study Guide")
    
elif selected == "Flashcards":
    st.title("Flashcards")
    st.text("Welcome to the Flashcards page")
    st.text("This is where you can generate flashcards from your notes")
    st.text("You can also view and edit your flashcards here")
    st.write("Click here to generate flashcards")
    st.button("Generate Flashcards")

elif selected == "Quiz":
    st.title("Quiz")
    st.text("Welcome to the Quiz page")
    st.text("This is where you can generate quizzes from your notes")
    st.text("You can also view and edit your quizzes here")
    st.write("Click here to generate a quiz")
    st.button("Generate Quiz")
    

    
    