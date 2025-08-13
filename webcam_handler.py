import cv2
import numpy as np
import base64
from typing import Optional, Callable
import threading
import time

class WebcamHandler:
    """Handle webcam operations for proctoring"""
    
    def __init__(self):
        self.cap = None
        self.is_recording = False
        self.frame_callback: Optional[Callable] = None
        self.current_frame = None
        
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera connection"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def start_monitoring(self, frame_callback: Callable):
        """Start continuous frame monitoring"""
        self.frame_callback = frame_callback
        self.is_recording = True
        
        def monitor_loop():
            while self.is_recording and self.cap:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    if self.frame_callback:
                        self.frame_callback(frame)
                time.sleep(0.1)  # 10 FPS for analysis
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def get_current_frame_b64(self) -> Optional[str]:
        """Get current frame as base64 string"""
        if self.current_frame is not None:
            _, buffer = cv2.imencode('.jpg', self.current_frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            return frame_b64
        return None
    
    def stop_monitoring(self):
        """Stop camera monitoring"""
        self.is_recording = False
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def capture_reference_image(self, save_path: str) -> bool:
        """Capture and save reference image"""
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite(save_path, frame)
                return True
        return False