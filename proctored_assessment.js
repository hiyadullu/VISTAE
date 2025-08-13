class ProctoredAssessment {
    constructor() {
        this.sessionId = null;
        this.currentQuestion = 0;
        this.totalQuestions = 0;
        this.userAnswers = [];
        this.webcamStream = null;
        this.violationCount = 0;
        
        this.init();
    }
    
    async init() {
        await this.setupWebcam();
        this.setupEventListeners();
    }
    
    async setupWebcam() {
        try {
            this.webcamStream = await navigator.mediaDevices.getUserMedia({ 
                video: true, 
                audio: false 
            });
            
            const webcamFeed = document.getElementById('webcamFeed');
            webcamFeed.srcObject = this.webcamStream;
            
            // Start monitoring frames
            this.startFrameMonitoring();
            
        } catch (error) {
            console.error('Error accessing webcam:', error);
            alert('Webcam access is required for proctored assessment');
        }
    }
    
    startFrameMonitoring() {
        setInterval(() => {
            this.captureAndAnalyzeFrame();
        }, 5000); // Analyze every 5 seconds
    }
    
    captureAndAnalyzeFrame() {
        const video = document.getElementById('webcamFeed');
        const canvas = document.getElementById('webcamCanvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        ctx.drawImage(video, 0, 0);
        
        // Convert to base64
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to backend for analysis (implement based on your backend)
        if (this.sessionId) {
            this.sendFrameForAnalysis(frameData);
        }
    }
    
    async sendFrameForAnalysis(frameData) {
        try {
            const response = await fetch('/api/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    webcam_frame: frameData,
                    answer: null // Just for frame analysis
                })
            });
            
            const result = await response.json();
            
            if (result.violations_detected && result.violations_detected.length > 0) {
                this.showViolationAlert(result.violations_detected);
            }
            
        } catch (error) {
            console.error('Error analyzing frame:', error);
        }
    }
    
    showViolationAlert(violations) {
        const violationsPanel = document.getElementById('violationsPanel');
        const violationsList = document.getElementById('violationsList');
        
        violations.forEach(violation => {
            const alertDiv = document.createElement('div');
            alertDiv.style.color = '#ff4444';
            alertDiv.style.marginBottom = '5px';
            alertDiv.textContent = this.getViolationMessage(violation);
            violationsList.appendChild(alertDiv);
        });
        
        violationsPanel.style.display = 'block';
        this.violationCount += violations.length;
        
        // Hide panel after 5 seconds
        setTimeout(() => {
            violationsPanel.style.display = 'none';
            violationsList.innerHTML = '';
        }, 5000);
    }
    
    getViolationMessage(violation) {
        const messages = {
            'no_face_detected': 'Please stay in camera view',
            'multiple_faces_detected': 'Multiple people detected',
            'looking_away': 'Please look at the screen',
            'phone_detected': 'Electronic device detected',
            'identity_mismatch': 'Identity verification failed'
        };
        return messages[violation] || 'Suspicious activity detected';
    }
    
    setupEventListeners() {
        document.getElementById('pdfInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                document.getElementById('startAssessment').style.display = 'block';
            }
        });
        
        document.getElementById('startAssessment').addEventListener('click', () => {
            this.startAssessment();
        });
    }
    
    async startAssessment() {
        try {
            // Start proctored session
            const sessionResponse = await fetch('/api/start-proctored-session', {
                method: 'POST'
            });
            const sessionData = await sessionResponse.json();
            this.sessionId = sessionData.session_id;
            
            // Upload PDF
            const fileInput = document.getElementById('pdfInput');
            const formData = new FormData();
            formData.append('pdf', fileInput.files[0]);
            formData.append('session_id', this.sessionId);
            formData.append('num_questions', '10');
            
            const uploadResponse = await fetch('/api/upload-pdf-proctored', {
                method: 'POST',
                body: formData
            });
            
            const uploadResult = await uploadResponse.json();
            
            if (uploadResult.success) {
                this.totalQuestions = uploadResult.num_questions;
                document.getElementById('uploadSection').style.display = 'none';
                this.loadQuestion(0);
            }
            
        } catch (error) {
            console.error('Error starting assessment:', error);
            alert('Failed to start assessment');
        }
    }
    
    async loadQuestion(questionNum) {
        try {
            const response = await fetch(`/api/get-question/${this.sessionId}/${questionNum}`);
            const questionData = await response.json();
            
            this.displayQuestion(questionData);
            
        } catch (error) {
            console.error('Error loading question:', error);
        }
    }
    
    displayQuestion(questionData) {
        const questionSection = document.getElementById('questionSection');
        questionSection.style.display = 'block';
        
        questionSection.innerHTML = `
            <div class="quiz-question-card">
                <h3>Question ${questionData.question_num} of ${questionData.total_questions}</h3>
                <p>${questionData.question}</p>
                
                <div class="options">
                    ${questionData.options.map((option, index) => `
                        <button class="option-button" onclick="assessment.selectOption(${index})">
                            ${String.fromCharCode(65 + index)}. ${option}
                        </button>
                    `).join('')}
                </div>
                
                <div style="margin-top: 20px;">
                    <button id="submitAnswer" onclick="assessment.submitAnswer()" disabled>
                        Submit Answer
                    </button>
                    <button onclick="assessment.nextQuestion()">
                        Next Question
                    </button>
                </div>
                
                <div style="margin-top: 10px; color: rgba(255,255,255,0.7);">
                    Progress: ${this.currentQuestion + 1}/${this.totalQuestions}
                </div>
            </div>
        `;
    }
    
    selectOption(optionIndex) {
        // Remove previous selection
        document.querySelectorAll('.option-button').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        document.querySelectorAll('.option-button')[optionIndex].classList.add('selected');
        document.getElementById('submitAnswer').disabled = false;
        
        this.selectedAnswer = optionIndex;
    }
    
    async submitAnswer() {
        if (this.selectedAnswer === undefined) return;
        
        try {
            const response = await fetch('/api/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    answer: this.selectedAnswer,
                    webcam_frame: null
                })
            });
            
            this.userAnswers.push(this.selectedAnswer);
            this.selectedAnswer = undefined;
            
            // Move to next question or finish
            if (this.currentQuestion < this.totalQuestions - 1) {
                this.currentQuestion++;
                this.loadQuestion(this.currentQuestion);
            } else {
                this.finishAssessment();
            }
            
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    }
    
    nextQuestion() {
        if (this.currentQuestion < this.totalQuestions - 1) {
            this.currentQuestion++;
            this.loadQuestion(this.currentQuestion);
        }
    }
    
    async finishAssessment() {
        try {
            const response = await fetch('/api/finish-proctored-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            this.displayResults(result);
            
        } catch (error) {
            console.error('Error finishing assessment:', error);
        }
    }
    
    displayResults(results) {
        const questionSection = document.getElementById('questionSection');
        
        questionSection.innerHTML = `
            <div class="quiz-question-card">
                <h2>🎓 Assessment Complete</h2>
                
                <div style="margin: 20px 0;">
                    <h3>Quiz Results:</h3>
                    <p>Score: ${results.quiz_score.toFixed(1)}% (${results.correct_answers}/${results.total_questions})</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Proctoring Report:</h3>
                    <p>Integrity Score: ${results.proctoring_report.integrity_score}%</p>
                    <p>Total Violations: ${results.proctoring_report.total_violations}</p>
                    <p>Session Duration: ${Math.round(results.proctoring_report.session_duration / 60)} minutes</p>
                    
                    <div style="margin-top: 15px;">
                        <h4>Violation Breakdown:</h4>
                        <ul>
                            <li>No Face Detected: ${results.proctoring_report.violation_breakdown.no_face}</li>
                            <li>Multiple Faces: ${results.proctoring_report.violation_breakdown.multiple_faces}</li>
                            <li>Looking Away: ${results.proctoring_report.violation_breakdown.looking_away}</li>
                            <li>Phone/Device Detected: ${results.proctoring_report.violation_breakdown.phone_detected}</li>
                        </ul>
                    </div>
                </div>
                
                <button onclick="window.location.reload()">Take Another Assessment</button>
            </div>
        `;
        
        // Stop webcam
        if (this.webcamStream) {
            this.webcamStream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize assessment when page loads
let assessment;
document.addEventListener('DOMContentLoaded', () => {
    assessment = new ProctoredAssessment();
});