import streamlit as st
import openai
import os
import PyPDF2

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define function to read a PDF document
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to ask a question based on the uploaded notes
def ask_question(notes, question):
    prompt = f"The following are lecture notes:\n\n{notes}\n\nQuestion: {question}\nAnswer in a clear and concise way."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to generate a quiz based on the uploaded notes
def generate_quiz(notes):
    prompt = f"Generate a multiple-choice quiz based on these lecture notes:\n\n{notes}\n\nInclude 5 questions with 4 options each."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to create flashcards
def generate_flashcards(notes):
    prompt = f"Generate flashcards with questions and answers from these lecture notes:\n\n{notes}\n\nCreate 5 flashcards."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Streamlit App
st.title("Learning Assistant App")

# Step 1: Upload lecture notes
uploaded_file = st.file_uploader("Upload your lecture notes (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    # Read the uploaded file
    if uploaded_file.type == "application/pdf":
        notes = read_pdf(uploaded_file)
    else:
        notes = uploaded_file.read().decode("utf-8")

    st.subheader("Lecture Notes Preview")
    st.write(notes[:500] + "...")  # Show the first 500 characters as a preview

    # Step 2: Ask a question
    st.subheader("Ask a Question")
    user_question = st.text_input("Type your question here:")
    
    if st.button("Get Answer"):
        if user_question:
            answer = ask_question(notes, user_question)
            st.write(f"AI Answer: {answer}")
        else:
            st.write("Please enter a question.")

    # Step 3: Generate a quiz
    st.subheader("Generate a Quiz")
    if st.button("Generate Quiz"):
        quiz = generate_quiz(notes)
        st.write(f"Quiz:\n\n{quiz}")

    # Step 4: Generate flashcards
    st.subheader("Generate Flashcards")
    if st.button("Generate Flashcards"):
        flashcards = generate_flashcards(notes)
        st.write(f"Flashcards:\n\n{flashcards}")

