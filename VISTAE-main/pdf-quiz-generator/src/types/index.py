from typing import List, Dict, Any

# Define the QuizQuestion type
class QuizQuestion:
    def __init__(self, question: str, options: List[str], correct_answer: int, explanation: str = ""):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

# Define the UserAnswer type
class UserAnswer:
    def __init__(self, question_id: int, selected_option: int):
        self.question_id = question_id
        self.selected_option = selected_option

# Define the QuizResult type
class QuizResult:
    def __init__(self, total_questions: int, correct_answers: int, user_answers: List[UserAnswer]):
        self.total_questions = total_questions
        self.correct_answers = correct_answers
        self.user_answers = user_answers

# Define a type for the database record of a quiz question
class QuizQuestionRecord:
    def __init__(self, id: int, question: str, options: List[str], correct_answer: int):
        self.id = id
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

# Define a type for the database record of a quiz result
class QuizResultRecord:
    def __init__(self, id: int, total_questions: int, correct_answers: int, user_answers: List[Dict[str, Any]]):
        self.id = id
        self.total_questions = total_questions
        self.correct_answers = correct_answers
        self.user_answers = user_answers