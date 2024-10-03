# import json
import requests
import streamlit as st
# from streamlit_lottie import st_lottie


st.set_page_config(
    page_title="Learning Assistant App"
)   



st.title ("Welcome to Learning Assistant App, your new Study Buddy")
st.text("You can upload your notes, ask questions to the AI, generate quizzes and review flashcards!")
st.text("Stay organized during the semester, be well prepared for CATs and Exams and pass with flying colours")

st.text("Let's get started!")
st.write("Upload your notes below")


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
    st.write(file_details)
    st.write("File Uploaded")
    st.write("You can now generate a summary of your notes, flashcards, study guide or quiz")
    if st.button("Generate Summary"):
        st.text("You have successfully uploaded your notes!")
        st.text("You can now get comprehensive summaries of your notes")
        st.button("Generate Summary")
    if st.button("Review Flashcards"):
        st.title("Welcome to Flashcards")
        st.text("Flashcards are a great way to review your notes and test your knowledge")  
        st.text("You can review your flashcards here")
        st.text("Click below to start reviewing your flashcards")
        st.button("Review Flashcards")
    if st.button("Generate Study Guide"):
        st.title ("Welcome to Study Guide")
        st.text("You can generate a study guide based on the amount of content you want to study and the time you have available")
        st.text("You can also generate a study guide based on the topics you want to study")
        st.text("Let's get started!")
        st.button("Generate Study Guide")
    if st.button("Generate Quiz"):
        st.text("Hi, I'm Quiz Bot! I'm here to help you generate quizzes from your notes")
        st.text("Please upload your notes below")
        st.text("I will generate a quiz for you based on the content of your notes")
        st.text("You can then review the quiz and test your knowledge")
        st.text("Let's get started!")
        st.button("Upload Notes")
    if st.button("Ask a Question"):
        st.textbox("Ask a question", "Type your question here")
        