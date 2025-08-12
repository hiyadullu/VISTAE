class PDFProcessor:
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        import PyPDF2
        
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()

    def clean_text(self, text: str) -> str:
        """Clean the extracted text for better processing."""
        import re
        
        # Remove extra whitespace and newlines
        cleaned_text = re.sub(r'\s+', ' ', text)
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text