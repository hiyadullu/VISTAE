import nltk
import random
import re
from typing import List, Dict
from dataclasses import dataclass
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')

except LookupError:
    nltk.data.path.append(r"C:/Users/hiyad/nltk_data")
    nltk.download('punkt', download_dir=r"C:/Users/hiyad/nltk_data")
    nltk.download('punkt_tab', download_dir=r"C:/Users/hiyad/nltk_data")
    nltk.download('stopwords', download_dir=r"C:/Users/hiyad/nltk_data")
    nltk.download('averaged_perceptron_tagger',download_dir="C:/Users/hiyad/nltk_data")
    nltk.download('averaged_perceptron_tagger_eng', download_dir="C:/Users/hiyad/nltk_data")

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str = ""

class FreeQuizGenerator:
    """Generate quizzes without requiring external APIs."""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def generate_quiz_from_text(self, text: str, num_questions: int = 10) -> List[QuizQuestion]:
        """Generate quiz questions using NLP techniques."""
        
        # Clean and prepare text
        sentences = sent_tokenize(text)
        sentences = [s for s in sentences if len(s.split()) > 5]  # Filter short sentences
        
        if len(sentences) < num_questions:
            num_questions = len(sentences)
        
        questions = []
        used_sentences = set()
        
        # Extract key information
        key_terms = self._extract_key_terms(text)
        
        for i in range(num_questions):
            # Select a sentence that hasn't been used
            available_sentences = [s for j, s in enumerate(sentences) if j not in used_sentences]
            if not available_sentences:
                break
                
            sentence = random.choice(available_sentences)
            sentence_idx = sentences.index(sentence)
            used_sentences.add(sentence_idx)
            
            # Generate different types of questions
            question_type = random.choice(['fill_blank', 'true_false', 'multiple_choice', 'definition'])
            
            if question_type == 'fill_blank':
                question = self._create_fill_blank_question(sentence, key_terms)
            elif question_type == 'true_false':
                question = self._create_true_false_question(sentence)
            elif question_type == 'multiple_choice':
                question = self._create_multiple_choice_question(sentence, key_terms)
            else:  # definition
                question = self._create_definition_question(sentence, key_terms)
            
            if question:
                questions.append(question)
        
        return questions
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract important terms from the text."""
        words = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        words = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        # Get POS tags
        pos_tags = pos_tag(words)
        
        # Extract nouns and proper nouns
        key_terms = [word for word, tag in pos_tags if tag.startswith('NN') or tag.startswith('JJ')]
        
        # Get most common terms
        term_freq = Counter(key_terms)
        return [term for term, freq in term_freq.most_common(50) if len(term) > 3]
    
    def _create_fill_blank_question(self, sentence: str, key_terms: List[str]) -> QuizQuestion:
        """Create a fill-in-the-blank question."""
        words = sentence.split()
        
        # Find a good word to blank out
        blank_word = None
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in key_terms and len(clean_word) > 3:
                blank_word = word
                break
        
        if not blank_word:
            return None
        
        # Create the question
        question_text = sentence.replace(blank_word, "______")
        question_text = f"Fill in the blank: {question_text}"
        
        # Create options
        correct_answer = re.sub(r'[^\w]', '', blank_word.lower())
        wrong_options = random.sample([term for term in key_terms if term != correct_answer], 3)
        
        options = [correct_answer] + wrong_options
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        return QuizQuestion(
            question=question_text,
            options=options,
            correct_answer=correct_idx,
            explanation=f"The correct answer is '{correct_answer}' as mentioned in the source text."
        )
    
    def _create_true_false_question(self, sentence: str) -> QuizQuestion:
        """Create a true/false question."""
        # Sometimes create a false statement by negating or changing key terms
        is_true = random.choice([True, False])
        
        if is_true:
            question_text = f"True or False: {sentence}"
            correct_idx = 0  # True
        else:
            # Create false version by modifying the sentence
            modified_sentence = self._modify_sentence_for_false(sentence)
            question_text = f"True or False: {modified_sentence}"
            correct_idx = 1  # False
        
        return QuizQuestion(
            question=question_text,
            options=["True", "False"],
            correct_answer=correct_idx,
            explanation="Based on the information provided in the source text."
        )
    
    def _modify_sentence_for_false(self, sentence: str) -> str:
        """Modify a sentence to make it false."""
        # Simple modifications - in a real implementation, this would be more sophisticated
        modifications = [
            ("is", "is not"),
            ("are", "are not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("should", "should not")
        ]
        
        for original, replacement in modifications:
            if f" {original} " in sentence:
                return sentence.replace(f" {original} ", f" {replacement} ")
        
        # If no simple modification works, add "not" after the first verb
        words = sentence.split()
        for i, word in enumerate(words):
            if word.lower() in ["is", "are", "was", "were", "can", "will", "should"]:
                words.insert(i + 1, "not")
                return " ".join(words)
        
        return sentence  # Return original if no modification possible
    
    def _create_multiple_choice_question(self, sentence: str, key_terms: List[str]) -> QuizQuestion:
        """Create a multiple choice question."""
        # Extract a key concept from the sentence
        words = word_tokenize(sentence)
        pos_tags = pos_tag(words)
        
        # Find important nouns or adjectives
        important_words = [word for word, tag in pos_tags if (tag.startswith('NN') or tag.startswith('JJ')) and len(word) > 3]
        
        if not important_words:
            return None
        
        focus_word = random.choice(important_words)
        
        question_text = f"According to the text, what is mentioned about '{focus_word}'?"
        
        # Create options
        correct_answer = sentence
        wrong_options = [
            f"{focus_word} is not discussed in the content",
            f"{focus_word} has different characteristics than described",
            f"The text provides insufficient information about {focus_word}"
        ]
        
        options = [correct_answer[:80] + "..." if len(correct_answer) > 80 else correct_answer] + wrong_options
        random.shuffle(options)
        correct_idx = options.index(correct_answer[:80] + "..." if len(correct_answer) > 80 else correct_answer)
        
        return QuizQuestion(
            question=question_text,
            options=options,
            correct_answer=correct_idx,
            explanation=f"This information about {focus_word} is directly stated in the source text."
        )
    
    def _create_definition_question(self, sentence: str, key_terms: List[str]) -> QuizQuestion:
        """Create a definition-style question."""
        # Find a key term in the sentence
        words = sentence.split()
        key_word = None
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in key_terms:
                key_word = clean_word
                break
        
        if not key_word:
            return None
        
        question_text = f"Based on the text, how is '{key_word}' best described?"
        
        # Extract context around the key word
        context = sentence
        
        # Create options
        correct_answer = f"As described in the provided context: {context[:60]}..."
        wrong_options = [
            f"{key_word} is not specifically defined in the text",
            f"The text contradicts common understanding of {key_word}",
            f"{key_word} is mentioned but not explained in detail"
        ]
        
        options = [correct_answer] + wrong_options
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        return QuizQuestion(
            question=question_text,
            options=options,
            correct_answer=correct_idx,
            explanation=f"The text provides specific information about {key_word} in this context."
        )




























