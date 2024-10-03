import streamlit as st

# Sample data
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