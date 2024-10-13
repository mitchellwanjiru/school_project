# import json
import requests
import streamlit as st
from streamlit_option_menu import option_menu
import cohere 
import os
import sqlite3
from PyPDF2 import PdfReader 
from db import connect_db, create_notes_table, create_flashcards_table, create_quiz_table, create_users_table, add_flashcard, add_note, add_quiz, get_all_users, get_user_flashcards, get_saved_notes, get_user_notes, get_user_quiz, update_user_progress, login_user, display_flashcards, display_notes, display_quizzes, display_users_table
#initialize tables
#create_flashcards_table(), create_notes_table(), create_quiz_table(), create_users_table()
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
    
    st.subheader("Upload New Notes")
    uploaded_file = st.file_uploader("Upload your notes (PDF or TXT)", type=["pdf", "txt"])
    
    user_id = 1
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            notes = ""
            for page in pdf_reader.pages:
                notes += page.extract_text()
        else:
            notes = uploaded_file.read().decode("utf-8")
        note_title = st.text_input("Enter the title for your notes",value = "Untitled notes")

        st.write("Here is a preview of your uploaded notes:")
        st.write(notes[:200] + "...")
        
        if st.button("Save notes"):
            add_note(user_id,note_title,notes)
            st.success("Notes saved successfully")
        

    
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
      
    

elif selected == "Study Guide":
    st.title("Study Guide")
    st.text("Welcome to the Study Guide page")
    st.text("This is where you can generate study guides from your notes")
    st.text("You can also view and edit your study guides here")
    st.write("Choose the notes to use to generate a study guide or describe what you want to study for")
    
 # function to generate a study guide
    def generate_study_guide():
        response = co.generate(
            model = 'command-xlarge-nightly',
            prompt = f"generate a clear and concise study guide based on the following notes\n\n{notes}\n\n",
            max_tokens=500,
        )
        study_guide = response.generations[0].text
        return study_guide
    
    
    
elif selected == "Flashcards":
    st.title("Generate and View Flashcards")
    st.text("Welcome to the Flashcards page")
    st.text("This is where you can generate flashcards from your notes")
    st.text("You can also view and edit your flashcards here")
    st.write("Click here to generate flashcards")

#function to generate flashcards
    def generate_flashcards(notes):
        response = co.generate(
        model='command-xlarge-nightly',
        prompt=f"generate 5 flashcards with questions and answers from the following notes:\n\n{notes}",
        max_tokens=200,
    )
        flashcards = response.generations[0].text
        return flashcards

#function to parse the generated text into question-answer pairs
    def parse_flashcards(flashcards_text):
        flashcards = []
        lines = flashcards_text.split("\n")
        for i in range(0, len(lines), 2):
            question = lines[i].strip()
            answer = lines[i + 1].strip() if i + 1 < len(lines) else ""
            flashcards.append(({"question": question, "answer": answer}))
        return flashcards

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

        

    # generate and save flashcards button
        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards..."):
                generated_flashcards = generate_flashcards(note_content)
                flashcards = parse_flashcards(generated_flashcards)
                user_id = 1
                for flashcard in flashcards:
                    question = flashcard["question"]
                    answer = flashcard["answer"]
                    add_flashcard(user_id, question, answer)
                    st.success("Flashcards generated and saved successfully!")
    else:
        st.write("No saved notes available.")

#display existing flashcards
    st.subheader("View Existing Flashcards")
    user_id = 1
    flashcards = get_user_flashcards(user_id)

    if flashcards:
        for question, answer in flashcards:
            st.write(f"Question: {question}")
        if st.button(f"Show Answer: {question}"):
            if answer:
                st.write(f"A: {answer[0]}")
            else:
                st.write("A:No answer available")
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

    

    
    