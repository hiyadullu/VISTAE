import PyPDF2
import fitz  # PyMuPDF - alternative PDF reader
from typing import Optional, List
import logging

class PDFProcessor:
    """Handles PDF text extraction with multiple fallback methods."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fallback method)."""
        try:
            text = ""
            pdf_document = fitz.open(pdf_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            pdf_document.close()
            return text.strip()
        except Exception as e:
            self.logger.error(f"PyMuPDF extraction failed: {e}")
            return ""
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using the best available method.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        # Try PyPDF2 first
        text = self.extract_text_pypdf2(pdf_path)
        
        # If PyPDF2 fails or returns empty, try PyMuPDF
        if not text:
            self.logger.info("Trying PyMuPDF as fallback...")
            text = self.extract_text_pymupdf(pdf_path)
        
        if not text:
            raise ValueError("Could not extract text from PDF using any method")
        
        return text
    
    def chunk_text(self, text: str, max_chunk_size: int = 3000) -> List[str]:
        """
        Split text into manageable chunks for quiz generation.
        
        Args:
            text (str): The full text to chunk
            max_chunk_size (int): Maximum size of each chunk
            
        Returns:
            List[str]: List of text chunks
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed limit, save current chunk
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and formatting issues.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (basic patterns)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        
        return text.strip()