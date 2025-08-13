from flask import Flask, request, jsonify, session
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os
from proctoring_system import ProctorAI
from webcam_handler import WebcamHandler
from quiz_generator import FreeQuizGenerator
from pdf_processor import PDFProcessor
import tempfile
import base64
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Global instances
active_sessions = {}

@app.route('/api/start-proctored-session', methods=['POST'])
def start_proctored_session():
    """Start a new proctored quiz session"""
    session_id = str(uuid.uuid4())
    
    # Initialize proctoring system
    proctor = ProctorAI()
    webcam = WebcamHandler()
    
    # Store session data
    active_sessions[session_id] = {
        'proctor': proctor,
        'webcam': webcam,
        'start_time': datetime.now(),
        'quiz_questions': [],
        'user_answers': [],
        'current_question': 0
    }
    
    proctor.start_session()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Proctored session started'
    })

@app.route('/api/upload-pdf-proctored', methods=['POST'])
def upload_pdf_proctored():
    """Upload PDF and generate quiz for proctored session"""
    session_id = request.form.get('session_id')
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file uploaded'}), 400
    
    pdf_file = request.files['pdf']
    num_questions = int(request.form.get('num_questions', 10))
    
    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_file.save(tmp_file.name)
            
            # Extract text and generate quiz
            pdf_processor = PDFProcessor()
            text = pdf_processor.extract_text(tmp_file.name)
            cleaned_text = pdf_processor.clean_text(text)
            
            quiz_generator = FreeQuizGenerator()
            questions = quiz_generator.generate_quiz_from_text(cleaned_text, num_questions)
            
            # Store questions in session
            active_sessions[session_id]['quiz_questions'] = [
                {
                    'question': q.question,
                    'options': q.options,
                    'correct_answer': q.correct_answer,
                    'explanation': q.explanation
                } for q in questions
            ]
            
            os.unlink(tmp_file.name)  # Clean up temp file
            
            return jsonify({
                'success': True,
                'message': f'Quiz generated with {len(questions)} questions',
                'num_questions': len(questions)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-question/<session_id>/<int:question_num>')
def get_question(session_id, question_num):
    """Get a specific question from the quiz"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    session_data = active_sessions[session_id]
    questions = session_data['quiz_questions']
    
    if question_num >= len(questions):
        return jsonify({'error': 'Question not found'}), 404
    
    question = questions[question_num]
    return jsonify({
        'question_num': question_num + 1,
        'total_questions': len(questions),
        'question': question['question'],
        'options': question['options']
    })

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit answer and analyze webcam frame"""
    data = request.json
    session_id = data.get('session_id')
    answer = data.get('answer')
    webcam_frame = data.get('webcam_frame')  # Base64 encoded frame
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    session_data = active_sessions[session_id]
    
    # Store answer
    session_data['user_answers'].append(answer)
    
    # Analyze webcam frame for violations
    if webcam_frame:
        try:
            # Decode base64 frame
            frame_data = base64.b64decode(webcam_frame.split(',')[1])
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Analyze frame
            proctor = session_data['proctor']
            analysis_result = proctor.analyze_frame(frame)
            
            return jsonify({
                'success': True,
                'violations_detected': analysis_result['violations'],
                'total_violations': analysis_result['total_violations']
            })
            
        except Exception as e:
            print(f"Error analyzing frame: {e}")
    
    return jsonify({'success': True})

@app.route('/api/finish-proctored-quiz', methods=['POST'])
def finish_proctored_quiz():
    """Finish quiz and generate proctoring report"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in active_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    session_data = active_sessions[session_id]
    proctor = session_data['proctor']
    
    # Calculate quiz score
    correct_answers = 0
    total_questions = len(session_data['quiz_questions'])
    
    for i, user_answer in enumerate(session_data['user_answers']):
        if i < total_questions:
            if user_answer == session_data['quiz_questions'][i]['correct_answer']:
                correct_answers += 1
    
    quiz_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Get proctoring report
    proctoring_report = proctor.get_session_report()
    
    # Clean up session
    del active_sessions[session_id]
    
    return jsonify({
        'quiz_score': quiz_score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'proctoring_report': proctoring_report,
        'session_completed': True
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)