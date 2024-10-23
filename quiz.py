import streamlit as st
import pymongo
from bson.objectid import ObjectId

# MongoDB Atlas connection details
MONGO_URI = "mongodb+srv://swethabalu276:Student123@cluster0.mongodb.net/vcc?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client.vcc  # Database name
quiz_collection = db.quizzes  # Collection name

# CRUD Operations
def create_quiz(question, options, answer):
    quiz_collection.insert_one({
        "question": question,
        "options": options,
        "answer": answer
    })

def read_quizzes():
    return list(quiz_collection.find())

def update_quiz(quiz_id, question, options, answer):
    quiz_collection.update_one(
        {"_id": ObjectId(quiz_id)},
        {"$set": {"question": question, "options": options, "answer": answer}}
    )

def delete_quiz(quiz_id):
    quiz_collection.delete_one({"_id": ObjectId(quiz_id)})

# Display quiz question and options
def display_question(question, options):
    st.subheader(question)
    user_answer = st.radio("Choose an option:", options)
    return user_answer

# Main application logic
def main():
    st.title("Interactive Quiz App")

    menu = ["Quiz", "Manage Quizzes"]
    choice = st.sidebar.selectbox("Select Activity", menu)

    if choice == "Quiz":
        # Fetch quizzes from the database
        quizzes = read_quizzes()
        if not quizzes:
            st.warning("No quizzes available.")
            return

        score = 0
        total_questions = len(quizzes)

        # Iterate through each quiz question
        for quiz in quizzes:
            question = quiz['question']
            options = quiz['options']
            correct_answer = quiz['answer']

            # Display the question
            user_answer = display_question(question, options)

            # If the user has answered
            if st.button("Submit Answer"):
                if user_answer:
                    if user_answer == correct_answer:
                        st.success("Correct answer!")
                        score += 1
                    else:
                        st.error(f"Incorrect! The correct answer was: {correct_answer}")
                else:
                    st.warning("Please select an answer.")

            st.write("---")  # Separator between questions

        # Final score display
        st.header(f"Your score: {score}/{total_questions}")
        if total_questions > 0:
            st.write(f"Your score percentage: {score / total_questions * 100:.2f}%")

    elif choice == "Manage Quizzes":
        st.subheader("CRUD Operations")

        # Create Quiz
        with st.form(key='create_quiz_form'):
            st.write("Add a New Quiz Question")
            question = st.text_input("Question")
            options = st.text_area("Options (comma-separated)").split(',')
            answer = st.text_input("Correct Answer")
            create_button = st.form_submit_button("Create Quiz")

            if create_button and question and options and answer:
                create_quiz(question, [opt.strip() for opt in options], answer)
                st.success("Quiz question created successfully!")

        # Read Quizzes
        st.write("Existing Quizzes")
        quizzes = read_quizzes()
        for quiz in quizzes:
            st.write(f"**{quiz['question']}**")
            st.write(f"Options: {', '.join(quiz['options'])}")
            st.write(f"Correct Answer: {quiz['answer']}")
            st.write(f"ID: {quiz['_id']}")
            
            # Update Quiz
            with st.form(key=f'update_quiz_form_{quiz["_id"]}'):
                st.write("Update Quiz Question")
                new_question = st.text_input("New Question", value=quiz['question'])
                new_options = st.text_area("New Options (comma-separated)", value=', '.join(quiz['options'])).split(',')
                new_answer = st.text_input("New Correct Answer", value=quiz['answer'])
                update_button = st.form_submit_button("Update Quiz")

                if update_button:
                    update_quiz(quiz['_id'], new_question, [opt.strip() for opt in new_options], new_answer)
                    st.success("Quiz question updated successfully!")

            # Delete Quiz
            if st.button(f"Delete Quiz {quiz['_id']}"):
                delete_quiz(quiz['_id'])
                st.success("Quiz question deleted successfully!")

# Run the app
if __name__ == "__main__":
    main()
