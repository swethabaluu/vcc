import streamlit as st
from pymongo import MongoClient
import random

# MongoDB Connection
CONNECTION_STRING = "mongodb+srv://swethabalu276:Student123@cluster0.tvrpc.mongodb.net/vcc?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)

# Specify the correct database and collection
db = client['vcc']  # Correct database name is 'vcc'
questions_collection = db['questions']  # Assuming 'questions' is the collection name

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
            "answer": "Paris"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Venus", "Jupiter"],
            "answer": "Mars"
        },
        {
            "question": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "answer": "Pacific"
        },
        {
            "question": "Who wrote 'To Kill a Mockingbird'?",
            "options": ["Harper Lee", "J.K. Rowling", "Ernest Hemingway", "Jane Austen"],
            "answer": "Harper Lee"
        },
        {
            "question": "What is the boiling point of water?",
            "options": ["90°C", "95°C", "100°C", "105°C"],
            "answer": "100°C"
        }
    ]
    
    # Insert questions if not already present in the database
    for question in questions:
        if questions_collection.count_documents({"question": question["question"]}) == 0:
            questions_collection.insert_one(question)

# Function to check if the user's answer is correct
def check_answer(user_answer, correct_answer):
    """Check if the user's answer is correct."""
    return user_answer == correct_answer

# Streamlit app
def quiz_app():
    # Insert sample questions into the database if not already present
    insert_sample_questions()

    st.title("Interactive Quiz App")

    # Fetch questions from MongoDB
    questions = fetch_questions()
    random.shuffle(questions)  # Shuffle questions for variety

    score = 0
    total_questions = len(questions)

    for i, question_data in enumerate(questions):
        st.subheader(f"Question {i+1}: {question_data['question']}")
        options = question_data['options']
        user_answer = st.radio("Select your answer:", options, key=i)
        
        if st.button(f"Submit Answer for Question {i+1}", key=f"submit{i}"):
            if check_answer(user_answer, question_data['answer']):
                st.success("Correct!")
                score += 1
            else:
                st.error(f"Wrong! The correct answer is: {question_data['answer']}")
    
    if st.button("Submit Quiz"):
        st.subheader(f"Your final score: {score}/{total_questions}")
        st.write("Thank you for playing!")

# Main execution
if __name__ == "__main__":
    quiz_app()
