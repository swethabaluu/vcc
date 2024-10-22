import os
import streamlit as st
from pymongo import MongoClient
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection
CONNECTION_STRING = os.getenv("MONGO_URI")
client = MongoClient(CONNECTION_STRING)

# Specify the correct database and collection
db = client['vcc']
questions_collection = db['questions']
answers_collection = db['user_answers']

# Function to fetch questions from MongoDB
def fetch_questions():
    return list(questions_collection.find())

# Function to insert sample questions into MongoDB if they don't exist
def insert_sample_questions():
    questions = [
        {"question": "What is the capital of France?", "options": ["Paris", "Berlin", "Madrid", "Rome"], "answer": ["Paris"]},
        {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Venus", "Jupiter"], "answer": ["Mars"]},
        {"question": "What is the largest ocean on Earth?", "options": ["Atlantic", "Indian", "Arctic", "Pacific"], "answer": ["Pacific"]},
        {"question": "Who wrote 'To Kill a Mockingbird'?", "options": ["Harper Lee", "J.K. Rowling", "Ernest Hemingway", "Jane Austen"], "answer": ["Harper Lee"]},
        {"question": "What is the boiling point of water?", "options": ["90°C", "95°C", "100°C", "105°C"], "answer": ["100°C"]}
    ]

    for question in questions:
        if questions_collection.count_documents({"question": question["question"]}) == 0:
            questions_collection.insert_one(question)

# Function to check if the user's answer is correct
def check_answer(user_answers, correct_answers):
    return set(user_answers) == set(correct_answers)

# Function to save user answers to MongoDB
def save_user_answer(user_name, question, user_answers, is_correct):
    answer_document = {
        "user_name": user_name,
        "question": question,
        "user_answers": user_answers,
        "is_correct": is_correct
    }
    answers_collection.insert_one(answer_document)

# Function to get leaderboard
def get_leaderboard():
    return pd.DataFrame(list(answers_collection.aggregate([
        {"$group": {"_id": "$user_name", "score": {"$sum": {"$cond": ["$is_correct", 1, 0]}}}},
        {"$sort": {"score": -1}}
    ])))

# Streamlit app
def quiz_app():
    insert_sample_questions()

    st.title("Interactive Quiz App")

    user_name = st.text_input("Enter your name:", "")

    if user_name:
        questions = fetch_questions()
        random.shuffle(questions)

        score = 0
        total_questions = len(questions)
        feedback = []

        for i, question_data in enumerate(questions):
            st.subheader(f"Question {i + 1}: {question_data['question']}")

            # Timer for each question
            start_time = time.time()
            selected_option = st.radio("Choose your answer:", question_data['options'], key=f"radio_{i}")

            # Timer Logic
            elapsed_time = 0
            while elapsed_time < 15:  # 15 seconds for each question
                elapsed_time = time.time() - start_time
                st.text(f"Time remaining: {15 - int(elapsed_time)} seconds")
                time.sleep(1)
                if st.button("Submit Answer", key=f"submit_answer_{i}"):  # Unique button key
                    break
            else:
                st.warning("Time's up! Moving to the next question.")
                selected_option = None  # No answer if time's up

            is_correct = selected_option in question_data['answer']
            feedback.append((question_data['question'], selected_option, is_correct))

            if is_correct:
                st.success("Correct!")
                score += 1
            else:
                st.error(f"Wrong! The correct answer is: {', '.join(question_data['answer'])}")

            save_user_answer(user_name, question_data['question'], [selected_option] if selected_option else [], is_correct)

        if st.button("Submit Quiz"):
            st.subheader(f"Your final score: {score}/{total_questions}")
            st.write("Thank you for playing!")
            st.write("User Feedback:")
            for q, ans, correct in feedback:
                st.write(f"Q: {q} | Your Answer: {ans if ans else 'No Answer'} | Correct: {'Yes' if correct else 'No'}")

            # Show Leaderboard
            st.write("Leaderboard:")
            leaderboard = get_leaderboard()
            st.write(leaderboard)

            # Visualization
            fig, ax = plt.subplots()
            leaderboard.set_index('_id')['score'].plot(kind='bar', ax=ax)
            ax.set_title('Leaderboard')
            ax.set_ylabel('Score')
            st.pyplot(fig)

# Main execution
if __name__ == "__main__":
    quiz_app()
