"""
Setup script for proctoring system
Run this once to download required models
"""

import urllib.request
import os
import zipfile

def download_dlib_models():
    """Download required dlib models"""
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Download shape predictor model
    shape_predictor_url = "https://github.com/italojs/facial-landmarks-recognition/raw/master/shape_predictor_68_face_landmarks.dat"
    shape_predictor_path = os.path.join(models_dir, "shape_predictor_68_face_landmarks.dat")
    
    if not os.path.exists(shape_predictor_path):
        print("Downloading facial landmark model...")
        urllib.request.urlretrieve(shape_predictor_url, shape_predictor_path)
        print("✓ Facial landmark model downloaded")
    else:
        print("✓ Facial landmark model already exists")

def setup_nltk_data():
    """Setup NLTK data for quiz generation"""
    import nltk
    
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        print("✓ NLTK data downloaded")
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")

if __name__ == "__main__":
    print("Setting up proctoring system...")
    download_dlib_models()
    setup_nltk_data()
    print("✓ Setup complete!")