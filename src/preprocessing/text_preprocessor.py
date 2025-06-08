"""
Text preprocessing utilities for cleaning and normalizing text data
before sentiment analysis.
"""

import re
import string
from typing import List, Optional
import logging

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Text preprocessing class for cleaning and normalizing text data.
    
    Provides various preprocessing options including:
    - HTML tag removal
    - URL and email removal  
    - Special character handling
    - Case normalization
    - Stop word removal
    - Stemming and lemmatization
    """
    
    def __init__(self, 
                 remove_urls: bool = True,
                 remove_emails: bool = True,
                 remove_html: bool = True,
                 remove_special_chars: bool = False,
                 lowercase: bool = True,
                 remove_stopwords: bool = False,
                 lemmatize: bool = False,
                 stem: bool = False):
        """
        Initialize text preprocessor with configuration options.
        
        Args:
            remove_urls: Remove URLs from text
            remove_emails: Remove email addresses
            remove_html: Remove HTML tags
            remove_special_chars: Remove special characters
            lowercase: Convert to lowercase
            remove_stopwords: Remove common stop words
            lemmatize: Apply lemmatization
            stem: Apply stemming
        """
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_html = remove_html
        self.remove_special_chars = remove_special_chars
        self.lowercase = lowercase
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.stem = stem
        
        # Initialize NLTK components if available
        if NLTK_AVAILABLE:
            self._setup_nltk()
        else:
            logger.warning("NLTK not available. Some preprocessing features will be disabled.")
            self.remove_stopwords = False
            self.lemmatize = False
            self.stem = False
    
    def _setup_nltk(self):
        """Setup NLTK components."""
        try:
            # Download required NLTK data if not already available
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        if self.remove_stopwords:
            try:
                nltk.data.find('corpora/stopwords')
                self.stop_words = set(stopwords.words('english'))
            except LookupError:
                logger.info("Downloading NLTK stopwords...")
                nltk.download('stopwords', quiet=True)
                self.stop_words = set(stopwords.words('english'))
        
        if self.lemmatize:
            try:
                nltk.data.find('corpora/wordnet')
                self.lemmatizer = WordNetLemmatizer()
            except LookupError:
                logger.info("Downloading NLTK wordnet...")
                nltk.download('wordnet', quiet=True)
                self.lemmatizer = WordNetLemmatizer()
        
        if self.stem:
            self.stemmer = PorterStemmer()
    
    def preprocess(self, text: str) -> str:
        """
        Apply all configured preprocessing steps to text.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Apply preprocessing steps in order
        processed_text = text
        
        if self.remove_html:
            processed_text = self._remove_html_tags(processed_text)
        
        if self.remove_urls:
            processed_text = self._remove_urls(processed_text)
        
        if self.remove_emails:
            processed_text = self._remove_emails(processed_text)
        
        if self.remove_special_chars:
            processed_text = self._remove_special_characters(processed_text)
        
        if self.lowercase:
            processed_text = processed_text.lower()
        
        # NLTK-based preprocessing
        if NLTK_AVAILABLE and (self.remove_stopwords or self.lemmatize or self.stem):
            processed_text = self._apply_nltk_preprocessing(processed_text)
        
        # Clean up extra whitespace
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        html_pattern = re.compile(r'<[^>]+>')
        return html_pattern.sub('', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.sub('', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return email_pattern.sub('', text)
    
    def _remove_special_characters(self, text: str) -> str:
        """Remove special characters, keeping only alphanumeric and basic punctuation."""
        # Keep letters, numbers, and basic punctuation
        pattern = re.compile(r'[^a-zA-Z0-9\s.,!?;:\-\'"()]')
        return pattern.sub('', text)
    
    def _apply_nltk_preprocessing(self, text: str) -> str:
        """Apply NLTK-based preprocessing (stopwords, lemmatization, stemming)."""
        # Tokenize text
        tokens = word_tokenize(text)
        
        # Remove stopwords
        if self.remove_stopwords and hasattr(self, 'stop_words'):
            tokens = [token for token in tokens if token.lower() not in self.stop_words]
        
        # Apply lemmatization
        if self.lemmatize and hasattr(self, 'lemmatizer'):
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Apply stemming
        if self.stem and hasattr(self, 'stemmer'):
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        return ' '.join(tokens)
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Preprocess a batch of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]
    
    def clean_for_analysis(self, text: str) -> str:
        """
        Apply minimal cleaning suitable for sentiment analysis.
        Preserves emoticons and sentiment-bearing punctuation.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text optimized for sentiment analysis
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove HTML but preserve structure
        text = self._remove_html_tags(text)
        
        # Remove URLs and emails (they don't contribute to sentiment)
        text = self._remove_urls(text)
        text = self._remove_emails(text)
        
        # Normalize whitespace but preserve line breaks for context
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
        
        # Clean up but preserve sentiment-bearing elements
        text = text.strip()
        
        return text 