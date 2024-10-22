import streamlit as st
from pymongo import MongoClient
import random

# MongoDB Connection
CONNECTION_STRING = "mongodb+srv://swethabalu276:Student123@cluster0.tvrpc.mongodb.net/vcc?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)

# Specify the correct database and collection
db = client['vcc']  # Correct database name is 'vcc'
questions_collection = db['questions']  # 'questions' collection
answers_collection = db['user_answers']  # New collection for storing user answers

# Function to fetch questions from MongoDB
def fetch_questions():
    """Fetch all questions from the MongoDB database."""
    return list(questions_collection.find())

# Function to insert a new question into MongoDB
def insert_sample_questions():
    """Insert sample questions into MongoDB if they don't already exist."""
    questions = [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "Berlin", "Madrid", "Rome"],
            "answer": ["Paris"]
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Venus", "Jupiter"],
            "answer": ["Mars"]
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "answer": ["Pacific"]
        },
        {
            "question": "Who wrote 'To Kill a Mockingbird'?",
            "options": ["Harper Lee", "J.K. Rowling", "Ernest Hemingway", "Jane Austen"],
            "answer": ["Harper Lee"]
        },
        {
            "question": "What is the boiling point of water?",
            "options": ["90°C", "95°C", "100°C", "105°C"],
            "answer": ["100°C"]
        }
    ]
    
    # Insert questions if not already present in the database
    for question in questions:
        if questions_collection.count_documents({"question": question["question"]}) == 0:
            questions_collection.insert_one(question)

# Function to check if the user's answer is correct
def check_answer(user_answers, correct_answers):
    """Check if the user's answer is correct."""
    return set(user_answers) == set(correct_answers)

# Function to save user answers to MongoDB
def save_user_answer(user_name, question, user_answers, is_correct):
    """Save the user's answer to MongoDB."""
    answer_document = {
        "user_name": user_name,
        "question": question,
        "user_answers": user_answers,
        "is_correct": is_correct
    }
    answers_collection.insert_one(answer_document)

# Streamlit app
def quiz_app():
    # Insert sample questions into the database if not already present
    insert_sample_questions()

    st.title("Interactive Quiz App")

    # Get user name
    user_name = st.text_input("Enter your name:", "")

    if user_name:
        # Fetch questions from MongoDB
        questions = fetch_questions()
        random.shuffle(questions)  # Shuffle questions for variety

        score = 0
        total_questions = len(questions)

        for i, question_data in enumerate(questions):
            st.subheader(f"Question {i+1}: {question_data['question']}")
            user_answers = []

            # Display options with checkboxes
            for option in question_data['options']:
                if st.checkbox(option, key=f"option_{i}_{option}"):
                    user_answers.append(option)

            if st.button(f"Submit Answer for Question {i+1}", key=f"submit{i}"):
                is_correct = check_answer(user_answers, question_data['answer'])
                if is_correct:
                    st.success("Correct!")
                    score += 1
                else:
                    st.error(f"Wrong! The correct answer is: {', '.join(question_data['answer'])}")

                # Save user's answer to the database
                save_user_answer(user_name, question_data['question'], user_answers, is_correct)

        if st.button("Submit Quiz"):
            st.subheader(f"Your final score: {score}/{total_questions}")
            st.write("Thank you for playing!")

# Main execution
if __name__ == "__main__":
    quiz_app()
