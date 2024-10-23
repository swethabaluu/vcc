import os
import streamlit as st
from pymongo import MongoClient
import random
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
CONNECTION_STRING = os.getenv("MONGO_URI")
client = MongoClient(CONNECTION_STRING)

# Specify the correct database and collections
db = client['vcc']
questions_collection = db['questions']
answers_collection = db['user_answers']
users_collection = db['users']  # Collection to store user credentials

# Function to fetch questions from MongoDB
def fetch_questions():
    """Fetch all questions from the MongoDB database."""
    return list(questions_collection.find())

# Function to insert sample questions into MongoDB
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

    for question in questions:
        if questions_collection.count_documents({"question": question["question"]}) == 0:
            questions_collection.insert_one(question)

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

# Function to register a new user
def register_user(username, password):
    """Register a new user in MongoDB."""
    if users_collection.count_documents({"username": username}) == 0:
        users_collection.insert_one({"username": username, "password": password})
        return True
    return False

# Function to authenticate a user
def authenticate_user(username, password):
    """Authenticate a user using username and password."""
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

# Function to visualize results
def visualize_results(user_name):
    """Visualize user's quiz results."""
    user_answers = list(answers_collection.find({"user_name": user_name}))
    
    if not user_answers:
        st.warning("No results to display.")
        return

    results = pd.DataFrame(user_answers)
    correct_counts = results.groupby('is_correct').size()

    # Plot results
    fig, ax = plt.subplots()
    correct_counts.plot(kind='bar', ax=ax)
    ax.set_title(f'Quiz Results for {user_name}')
    ax.set_xlabel('Correct/Incorrect')
    ax.set_ylabel('Number of Questions')
    ax.set_xticklabels(['Incorrect', 'Correct'], rotation=0)
    st.pyplot(fig)

# Streamlit app
def quiz_app():
    insert_sample_questions()

    st.title("Interactive Quiz App")
    
    # User Authentication
    st.sidebar.title("User Authentication")
    option = st.sidebar.selectbox("Select an option:", ["Sign In", "Sign Up"])
    
    username = st.sidebar.text_input("Username:")
    password = st.sidebar.text_input("Password:", type='password')

    # Sign up option
    if option == "Sign Up":
        if st.sidebar.button("Register"):
            if register_user(username, password):
                st.sidebar.success("Registration successful! You can now sign in.")
            else:
                st.sidebar.error("Username already exists.")
    
    # Sign in option
    elif option == "Sign In":
        if st.sidebar.button("Login"):
            if authenticate_user(username, password):
                st.sidebar.success("Login successful!")
            else:
                st.sidebar.error("Invalid username or password.")
    
    # Proceed to quiz if authenticated
    if authenticate_user(username, password):
        questions = fetch_questions()
        random.shuffle(questions)

        total_questions = len(questions)

        # Session state to track the score
        if "score" not in st.session_state:
            st.session_state.score = 0

        score = st.session_state.score
        user_answers = {}

        # Display all 5 questions with options
        st.subheader("Please answer all questions:")
        for i, question_data in enumerate(questions[:5]):
            st.markdown(f"### Question {i + 1}: {question_data['question']}")
            
            # Use radio buttons to select one option per question
            user_answers[question_data['question']] = st.radio(
                label="Select your answer:",
                options=question_data['options'],
                key=f"question_{i}"
            )

        # Submit Button at the end of the quiz
        if st.button("Submit Quiz"):
            # Calculate the score and save each answer
            for i, question_data in enumerate(questions[:5]):
                selected_option = user_answers[question_data['question']]
                correct = selected_option == question_data['answer'][0]
                
                if correct:
                    st.session_state.score += 1
                    st.success(f"Question {i + 1}: Correct! The answer is {question_data['answer'][0]}.")
                else:
                    st.error(f"Question {i + 1}: Wrong! The correct answer is {question_data['answer'][0]}.")

                # Save user's answer to the database
                save_user_answer(username, question_data['question'], [selected_option], correct)

            # Display final score
            st.subheader(f"Your final score: {st.session_state.score}/{total_questions}")
            st.write("Thank you for playing!")
            visualize_results(username)

# Main execution
if __name__ == "__main__":
    quiz_app()
