import streamlit as st
import tempfile
import os
from pdf_processor import PDFProcessor
from quiz_generator import FreeQuizGenerator, QuizQuestion
from db.database import Database
from typing import List

# Initialize session state
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False

# Initialize database
db = Database()

def process_pdf_to_quiz(uploaded_file, num_questions: int = 10):
    """Process uploaded PDF and convert to quiz."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Extract text from PDF
        pdf_processor = PDFProcessor()
        text = pdf_processor.extract_text(tmp_file_path)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Clean the extracted text
        cleaned_text = pdf_processor.clean_text(text)
        
        # Generate quiz
        quiz_generator = FreeQuizGenerator()
        questions = quiz_generator.generate_quiz_from_text(cleaned_text, num_questions)
        
        # Save questions to database
        db.save_quiz_questions(questions)
        
        return questions, cleaned_text
        
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return [], ""

def display_quiz_question(question: QuizQuestion, question_num: int):
    """Display a single quiz question."""
    st.subheader(f"Question {question_num + 1}")
    st.write(question.question)
    
    # Display options
    selected_option = st.radio(
        "Choose your answer:",
        options=range(len(question.options)),
        format_func=lambda x: f"{chr(65 + x)}. {question.options[x]}",
        key=f"question_{question_num}"
    )
    
    return selected_option

def main():
    st.title(" PDF to Quiz Generator")
    st.subheader(" Free AI-Powered Quiz Generation")
    
    # Sidebar for configuration
    st.sidebar.header(" Configuration")
    num_questions = st.sidebar.slider("Number of Questions", 5, 20, 10)
    
    # Information about the free method
    st.sidebar.info("""
    🆓 **Free Quiz Generator**
    - No API key required
    - Uses advanced NLP techniques
    - Multiple question types:
      • Fill in the blanks
      • True/False
      • Multiple choice
    - Instant generation
    """)
    
    # File upload
    uploaded_file = st.file_uploader(" Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.success(f" File uploaded: {uploaded_file.name}")
        
        if st.button("Generate Quiz", type="primary"):
            with st.spinner(" Processing PDF and generating quiz..."):
                questions, extracted_text = process_pdf_to_quiz(uploaded_file, num_questions)
                
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.current_question = 0
                    st.session_state.user_answers = []
                    st.session_state.quiz_completed = False
                    st.success(f"🎉 Quiz generated successfully with {len(questions)} questions!")
                    st.rerun()
                else:
                    st.error("❌ Could not generate quiz. Please try with a different PDF.")
    else:
        st.info(" Please upload a PDF file to get started!")
    
    # Display quiz if generated
    if st.session_state.quiz_questions:
        if not st.session_state.quiz_completed:
            # Show current question
            current_q = st.session_state.current_question
            question = st.session_state.quiz_questions[current_q]
            
            selected_answer = display_quiz_question(question, current_q)
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if current_q > 0:
                    if st.button("Previous"):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col2:
                if st.button("Submit Answer"):
                    # Store answer
                    if len(st.session_state.user_answers) <= current_q:
                        st.session_state.user_answers.append(selected_answer)
                    else:
                        st.session_state.user_answers[current_q] = selected_answer
                    
                    # Move to next question or finish quiz
                    if current_q < len(st.session_state.quiz_questions) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.session_state.quiz_completed = True
                        st.rerun()
            
            with col3:
                if current_q < len(st.session_state.quiz_questions) - 1:
                    if st.button("Next"):
                        st.session_state.current_question += 1
                        st.rerun()
        
        else:
            # Show results
            st.subheader("Quiz Results")
            
            correct_answers = 0
            total_questions = len(st.session_state.quiz_questions)
            
            for i, (question, user_answer) in enumerate(zip(st.session_state.quiz_questions, st.session_state.user_answers)):
                is_correct = user_answer == question.correct_answer
                if is_correct:
                    correct_answers += 1
                
                st.write(f"**Question {i + 1}:** {question.question}")
                st.write(f"Your answer: {chr(65 + user_answer)}. {question.options[user_answer]}")
                st.write(f"Correct answer: {chr(65 + question.correct_answer)}. {question.options[question.correct_answer]}")
                
                if is_correct:
                    st.success("✓ Correct!")
                else:
                    st.error("✗ Incorrect")
                
                if question.explanation:
                    st.info(f"Explanation: {question.explanation}")
                
                st.divider()
            
            # Final score
            score_percentage = (correct_answers / total_questions) * 100
            st.subheader(f"Final Score: {correct_answers}/{total_questions} ({score_percentage:.1f}%)")
            
            # Reset button
            if st.button("Generate New Quiz"):
                st.session_state.quiz_questions = []
                st.session_state.current_question = 0
                st.session_state.user_answers = []
                st.session_state.quiz_completed = False
                st.rerun()

if __name__ == "__main__":
    main()