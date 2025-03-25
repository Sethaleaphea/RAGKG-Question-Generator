import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from core.question_generator import generate_questions

st.title("AI-Powered Question Generator")

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = []

# User Inputs
topic = st.text_input("Enter the topic:")
num_questions = st.number_input("Number of Questions:", min_value=1, max_value=10, step=1)
difficulty = st.selectbox("Select Difficulty:", ["Easy", "Medium", "Hard"])

# Add "Fill in the Blank" to question type selection
question_type = st.selectbox("Select Question Type:", ["Multiple Choice", "True/False", "Open Ended", "Fill in the Blank", "Matching"])

# Generate button
if st.button("Generate Questions"):
    with st.spinner("Generating questions, please wait..."):
        try:
            # Ensure generate_questions now also stores to Neo4j or adjusts as needed
            generated_questions = generate_questions(topic, num_questions, difficulty, question_type)
            
            # Store the questions in session state
            st.session_state.questions = generated_questions
            
            st.success("Questions generated successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Display generated questions
if st.session_state.questions:
    st.subheader("Generated Questions")
    for i, question in enumerate(st.session_state.questions, 1):
        st.write(f"{i}. {question}")
