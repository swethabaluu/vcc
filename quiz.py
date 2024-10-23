import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import random

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

# Function to display quiz and get user answers using buttons
def quiz(username):
    st.title("Quiz Time!")

    # Fetch questions from the database
    questions = fetch_questions()
    random.shuffle(questions)

    # Session state to store answers
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = [None] * 10

    # Iterate through all questions, display them with answer options
    for i, question in enumerate(questions[:10]):
        st.subheader(f"Question {i+1}: {question['question']}")

        # Use buttons to allow users to select answers
        st.session_state.user_answers[i] = st.radio(
            f"Select an answer for Question {i+1}",
            options=question['options'],
            index=question['options'].index(st.session_state.user_answers[i]) if st.session_state.user_answers[i] else 0
        )

    # Submit Button at the end of the quiz
    if st.button("Submit Quiz"):
        if None in st.session_state.user_answers:
            st.error("Please answer all questions before submitting.")
        else:
            user_answers = []
            for i, question in enumerate(questions[:10]):
                user_answers.append({
                    "question": question['question'],
                    "user_answer": st.session_state.user_answers[i],
                    "correct_answer": question['answer']
                })

            score = save_user_answers(username, user_answers)
            st.success("Quiz submitted successfully!")
            st.write(f"Your final score is {score}/10.")
            st.write("You can view your score anytime from the 'View Score' option in the sidebar.")

# View score of logged-in user
def view_score(username):
    st.title("Your Quiz Score")
    user_results = answers_collection.find({"username": username}).sort("score", -1)
    if user_results.count() > 0:
        latest_result = user_results[0]
        st.write(f"Your latest score is {latest_result['score']}/10.")
        for answer in latest_result['answers']:
            st.write(f"Q: {answer['question']}, Your Answer: {answer['user_answer']}, Correct Answer: {answer['correct_answer']}")
    else:
        st.warning("You haven't completed any quizzes yet.")

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
                # Show options to either take a quiz or view score
                menu_option = st.sidebar.selectbox("Menu", ["Take Quiz", "View Score"])
                if menu_option == "Take Quiz":
                    quiz(username)  # Display quiz questions
                elif menu_option == "View Score":
                    view_score(username)  # Show user's score
            else:
                st.sidebar.error("Invalid credentials! Please try again.")

if __name__ == "__main__":
    quiz_app()
