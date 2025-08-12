# PDF to Quiz Generator

## Overview
The PDF to Quiz Generator is a web application that allows users to upload PDF documents and generate quizzes based on the content of those documents. The application utilizes advanced Natural Language Processing (NLP) techniques to create various types of questions, including multiple choice, true/false, and fill-in-the-blank.

## Features
- Upload PDF files to generate quizzes.
- Supports multiple question types.
- Instant quiz generation using AI-powered algorithms.
- User-friendly interface built with Streamlit.
- Stores quiz questions, user answers, and results in a database.

## Project Structure
```
pdf-quiz-generator
├── src
│   ├── main.py               # Entry point of the application
│   ├── pdf_processor.py       # Handles PDF text extraction and cleaning
│   ├── quiz_generator.py       # Generates quiz questions from text
│   ├── db
│   │   ├── __init__.py        # Initializes the database package
│   │   ├── models.py          # Defines database models for quizzes
│   │   └── database.py        # Database connection and interaction logic
│   └── types
│       └── index.py          # Custom types and interfaces
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd pdf-quiz-generator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   streamlit run src/main.py
   ```

2. Upload a PDF file using the provided interface.

3. Click on "Generate Quiz" to create a quiz based on the content of the PDF.

4. Answer the questions and submit your answers to see your results.

## Database
The application uses a database to store quiz questions, user answers, and results. The database models are defined in `src/db/models.py`, and the connection logic is handled in `src/db/database.py`.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.