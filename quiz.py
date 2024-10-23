import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import random
import pandas as pd

# Load environment variables for MongoDB connection
load_dotenv()

# MongoDB connection
CONNECTION_STRING = os.getenv("MONGO_URI")
client = MongoClient(CONNECTION_STRING)

# Specify the database and collections
db = client['vcc']
users_collection = db['users']
answers_collection = db['user_answers']
questions_collection = db['questions']

# Sample Questions to insert
def insert_sample_questions():
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
        },
        # Add 5 more questions to make it 10 in total
        {
            "question": "Which country is known as the Land of Rising Sun?",
            "options": ["China", "Japan", "South Korea", "Vietnam"],
            "answer": "Japan"
        },
        {
            "question": "Who discovered gravity?",
            "options": ["Isaac Newton", "Albert Einstein", "Galileo", "Marie Curie"],
            "answer": "Isaac Newton"
        },
        {
            "question": "What is the chemical symbol for gold?",
            "options": ["Go", "G", "Au", "Ag"],
            "answer": "Au"
        },
        {
            "question": "Which is the smallest continent?",
            "options": ["Asia", "Europe", "Australia", "Antarctica"],
            "answer": "Australia"
        },
        {
            "question": "What is the square root of 64?",
            "options": ["6", "7", "8", "9"],
            "answer": "8"
        }
    ]
    for question in questions:
        if questions_collection.count_documents({"question": question["question"]}) == 0:
            questions_collection.insert_one(question)

# Sign up function
def register_user(username, password):
    if users_collection.count_documents({"username": username}) == 0:
        users_collection.insert_one({"username": username, "password": password})
        return True
    return False

# Sign in function
def authenticate_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

# Function to save user answers and calculate score
def save_user_answers(username, answers):
    total_score = 0
    correct_answers = 0
    for question in answers:
        if question['user_answer'] == question['correct_answer']:
            correct_answers += 1
    total_score = correct_answers

    # Store the result in the database
    answers_collection.insert_one({
        "username": username,
        "score": total_score,
        "answers": answers
    })

    return total_score

# Fetch all questions from MongoDB
def fetch_questions():
    return list(questions_collection.find())

# Function to display quiz and get user answers
def quiz(username):
    st.title("Quiz Time!")

    # Fetch questions from the database
    questions = fetch_questions()
    random.shuffle(questions)

    user_answers = []
    
    # Iterate through questions
    for i, question in enumerate(questions[:10]):
        st.subheader(f"Question {i+1}: {question['question']}")
        user_answer = st.radio(
            f"Select an answer for Question {i+1}", 
            question['options'], 
            key=f"question_{i}"
        )
        user_answers.append({
            "question": question['question'],
            "user_answer": user_answer,
            "correct_answer": question['answer']
        })

    # Submit Button at the end of the quiz
    if st.button("Submit Quiz"):
        score = save_user_answers(username, user_answers)
        st.success(f"Your final score is {score}/10.")
        
        # Option to see the reflection in DB (Optional visualization)
        view_score(username)

# View score of logged-in user
def view_score(username):
    user_results = answers_collection.find({"username": username}).sort("score", -1)
    if user_results:
        for result in user_results:
            st.write(f"Your Score: {result['score']}")
            for answer in result['answers']:
                st.write(f"Q: {answer['question']}, Your Answer: {answer['user_answer']}, Correct Answer: {answer['correct_answer']}")

# Main Streamlit App
def quiz_app():
    insert_sample_questions()  # Insert questions if they don't already exist
    
    st.sidebar.title("Authentication")
    
    # Sign up or Sign in Option
    auth_option = st.sidebar.selectbox("Choose an option", ["Sign Up", "Sign In"])

    if auth_option == "Sign Up":
        new_username = st.sidebar.text_input("Enter Username:")
        new_password = st.sidebar.text_input("Enter Password:", type="password")
        if st.sidebar.button("Register"):
            if register_user(new_username, new_password):
                st.sidebar.success("Registration successful! You can now sign in.")
            else:
                st.sidebar.error("Username already exists. Please choose another.")

    if auth_option == "Sign In":
        username = st.sidebar.text_input("Username:")
        password = st.sidebar.text_input("Password:", type="password")
        if st.sidebar.button("Login"):
            if authenticate_user(username, password):
                st.sidebar.success(f"Welcome {username}! You are logged in.")
                quiz(username)  # Call quiz function after successful login
            else:
                st.sidebar.error("Invalid credentials! Please try again.")

if __name__ == "__main__":
    quiz_app()
