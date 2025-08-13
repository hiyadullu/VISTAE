import cv2
import numpy as np
import dlib
import face_recognition
import time
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import threading
import queue

class ProctorAI:
    """AI-powered proctoring system using computer vision"""
    
    def __init__(self):
        # Initialize face detection and recognition
        self.face_detector = dlib.get_frontal_face_detector()
        self.shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        
        # Proctoring flags and counters
        self.violations = {
            'multiple_faces': 0,
            'no_face': 0,
            'looking_away': 0,
            'phone_detected': 0,
            'suspicious_movement': 0
        }
        
        self.session_start_time = None
        self.last_face_encoding = None
        self.violation_timestamps = []
        
    def start_session(self, reference_image_path: Optional[str] = None):
        """Start proctoring session"""
        self.session_start_time = datetime.now()
        self.violations = {k: 0 for k in self.violations.keys()}
        self.violation_timestamps = []
        
        if reference_image_path:
            self.load_reference_face(reference_image_path)
    
    def load_reference_face(self, image_path: str):
        """Load reference face for identity verification"""
        try:
            reference_image = face_recognition.load_image_file(image_path)
            self.last_face_encoding = face_recognition.face_encodings(reference_image)[0]
        except Exception as e:
            print(f"Error loading reference face: {e}")
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """Analyze a single frame for violations"""
        violations_detected = []
        
        # Convert to RGB for face_recognition library
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = face_recognition.face_locations(rgb_frame)
        
        if len(faces) == 0:
            self.violations['no_face'] += 1
            violations_detected.append('no_face_detected')
        elif len(faces) > 1:
            self.violations['multiple_faces'] += 1
            violations_detected.append('multiple_faces_detected')
        else:
            # Single face detected - check for other violations
            face_encodings = face_recognition.face_encodings(rgb_frame, faces)
            if face_encodings and self.last_face_encoding is not None:
                # Check identity
                matches = face_recognition.compare_faces([self.last_face_encoding], face_encodings[0])
                if not matches[0]:
                    violations_detected.append('identity_mismatch')
            
            # Check gaze direction and head pose
            if self.check_looking_away(frame, faces[0]):
                self.violations['looking_away'] += 1
                violations_detected.append('looking_away')
        
        # Check for phone/electronic devices
        if self.detect_phone(frame):
            self.violations['phone_detected'] += 1
            violations_detected.append('phone_detected')
        
        # Log violations with timestamp
        if violations_detected:
            self.violation_timestamps.append({
                'timestamp': datetime.now().isoformat(),
                'violations': violations_detected
            })
        
        return {
            'violations': violations_detected,
            'total_violations': sum(self.violations.values()),
            'face_count': len(faces)
        }
    
    def check_looking_away(self, frame: np.ndarray, face_location: Tuple) -> bool:
        """Check if person is looking away from camera"""
        top, right, bottom, left = face_location
        face_region = frame[top:bottom, left:right]
        
        # Use eye aspect ratio and head pose estimation
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector(gray)
        
        for face in faces:
            landmarks = self.shape_predictor(gray, face)
            
            # Calculate eye aspect ratio
            left_ear = self.eye_aspect_ratio(landmarks, range(36, 42))
            right_ear = self.eye_aspect_ratio(landmarks, range(42, 48))
            
            # If eyes are looking away or closed for too long
            if (left_ear < 0.2 or right_ear < 0.2):
                return True
                
        return False
    
    def eye_aspect_ratio(self, landmarks, eye_points):
        """Calculate eye aspect ratio for blink detection"""
        points = np.array([[landmarks.part(i).x, landmarks.part(i).y] for i in eye_points])
        
        # Calculate distances
        A = np.linalg.norm(points[1] - points[5])
        B = np.linalg.norm(points[2] - points[4])
        C = np.linalg.norm(points[0] - points[3])
        
        return (A + B) / (2.0 * C)
    
    def detect_phone(self, frame: np.ndarray) -> bool:
        """Basic phone detection using template matching"""
        # This would need a more sophisticated model in production
        # For now, using simple edge detection to identify rectangular objects
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 10000:  # Phone-like size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                if 0.4 < aspect_ratio < 0.8:  # Phone-like aspect ratio
                    return True
        return False
    
    def get_session_report(self) -> Dict:
        """Generate final proctoring report"""
        session_duration = (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0
        
        return {
            'session_duration': session_duration,
            'total_violations': sum(self.violations.values()),
            'violation_breakdown': self.violations,
            'violation_timeline': self.violation_timestamps,
            'integrity_score': max(0, 100 - sum(self.violations.values()) * 5),
            'session_start': self.session_start_time.isoformat() if self.session_start_time else None
        }