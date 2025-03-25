import os
import sys
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from groq import Groq
from core.rag import search_topic, store_generated_question
from config.config import API_KEY

def generate_questions(topic, num_questions=3, difficulty='Medium', question_type='Multiple Choice'):
    client = Groq(api_key=API_KEY)  # Load API key from config
    retrieved_chunks = search_topic(topic)

    if not retrieved_chunks:
        return ["No relevant context found. Please refine your topic."]
    
    # Validate question type
    valid_question_types = ["True/False", "Multiple Choice", "Open Ended", "Fill in the Blank", "Matching"]
    if question_type not in valid_question_types:
        return [f"Error: Unsupported question type. Please choose from {', '.join(valid_question_types)}."]
    
    # Validate difficulty
    valid_difficulties = ["Easy", "Medium", "Hard"]
    if difficulty not in valid_difficulties:
        return [f"Error: Unsupported difficulty level. Please choose from {', '.join(valid_difficulties)}."]
    
    questions = []
    available_chunks = len(retrieved_chunks)
    num_questions = min(num_questions, available_chunks)
    
    # Define question templates
    question_templates = {
        "True/False": [
            "You are an AI that generates True/False questions.\n"
            "Context: {context}\n"
            "Generate a {difficulty} level True/False question.\n"
            "Format:\n"
            "Statement: [Generated statement]\n"
            "True or False?\n"
            "Correct Answer: [True or False]",
        ],
        "Multiple Choice": [
            "You are an AI that generates multiple-choice questions with four options.\n"
            "Context: {context}\n"
            "Generate a {difficulty} level multiple-choice question.\n"
            "Format:\n"
            "Question: [Generated question]\n"
            "A) [Option 1]\n"
            "B) [Option 2]\n"
            "C) [Option 3]\n"
            "D) [Option 4]\n"
            "Correct Answer: [A/B/C/D] [Full Text of Correct Option]",
        ],
        "Open Ended": [
            "You are an AI that generates open-ended questions.\n"
            "Context: {context}\n"
            "Generate a {difficulty} level open-ended question that encourages a detailed response.\n"
            "Format:\n"
            "Question: [Generated question]",
        ],
        "Fill in the Blank": [
            "You are an AI that generates fill-in-the-blank questions.\n"
            "Context: {context}\n"
            "Generate a {difficulty} level fill-in-the-blank question.\n"
            "Format:\n"
            "Question: [Generated question with a blank]\n"
            "Correct Answer: [The correct word/phrase that fills in the blank]"
        ],
        "Matching": [
            "You are an AI that generates matching questions.\n"
            "Context: {context}\n"
            "Generate a {difficulty} level matching question with five pairs.\n"
            "Format:\n"
            "Question: Match the items in Column A with their correct pairs in Column B.\n"
            "**Column A:**\n"
            "1) [Item 1]\n"
            "2) [Item 2]\n"
            "3) [Item 3]\n"
            "4) [Item 4]\n"
            "5) [Item 5]\n\n"
            "**Column B:**\n"
            "A) [Definition for Item 1]\n"
            "B) [Definition for Item 2]\n"
            "C) [Definition for Item 3]\n"
            "D) [Definition for Item 4]\n"
            "E) [Definition for Item 5]\n\n"
            "**Correct Matches:** 1 → [A], 2 → [B], 3 → [C], 4 → [D], 5 → [E]"
        ]
    }
    
    selected_template = random.choice(question_templates[question_type])

    for i in range(num_questions):
        context = retrieved_chunks[i % available_chunks]
        prompt = selected_template.format(context=context, difficulty=difficulty)

        # Generate response from the AI model
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        # Extract the generated question
        response_text = chat_completion.choices[0].message.content.strip()
        correct_answer = None  # Default

        # Extract correct answer for Fill in the Blank and Matching Questions
        if question_type == "Fill in the Blank":
            parts = response_text.split("\nCorrect Answer: ")
            if len(parts) == 2:
                question_text = parts[0].strip()
                correct_answer = parts[1].strip()
            else:
                question_text = response_text  # If format is incorrect, store as-is
        elif question_type == "Matching":
            parts = response_text.split("\n**Correct Matches:** ")
            if len(parts) == 2:
                question_text = parts[0].strip()
                correct_answer = parts[1].strip()
                # Validate if the matching answers are in the correct format
                correct_answer = correct_answer.replace(" →", ":")  # Ensure the " → " gets formatted to ":"
            else:
                question_text = response_text  # If format is incorrect, store as-is
        else:
            question_text = response_text

        # Store in the database
        store_generated_question(topic, question_text, difficulty, question_type, correct_answer)

        # Append formatted question
        if question_type in ["Fill in the Blank", "Matching"]:
            questions.append(f"{question_text}\n\n**Answer:** {correct_answer}")
        else:
            questions.append(question_text)

    return questions
