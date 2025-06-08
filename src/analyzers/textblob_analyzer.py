"""
TextBlob sentiment analyzer.
Uses TextBlob's built-in sentiment analysis which is based on movie reviews.
"""

from typing import Dict
from textblob import TextBlob
from ..analyzers.sentiment_analyzer import SentimentLabel


class TextBlobAnalyzer:
    """
    TextBlob sentiment analyzer wrapper.
    
    TextBlob provides a simple API for diving into common natural language 
    processing (NLP) tasks. Its sentiment analysis returns polarity and subjectivity.
    """
    
    def __init__(self):
        """Initialize TextBlob analyzer."""
        pass
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get polarity (-1 to 1) and subjectivity (0 to 1)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment based on polarity
        if polarity > 0.1:
            sentiment = SentimentLabel.POSITIVE
            confidence = polarity
        elif polarity < -0.1:
            sentiment = SentimentLabel.NEGATIVE
            confidence = abs(polarity)
        else:
            sentiment = SentimentLabel.NEUTRAL
            confidence = 1 - abs(polarity)
        
        # Convert polarity to probability-like scores
        # Normalize polarity from [-1, 1] to [0, 1] range
        normalized_polarity = (polarity + 1) / 2
        
        # Create score distribution
        if polarity > 0:
            pos_score = normalized_polarity
            neg_score = 1 - normalized_polarity
            neu_score = (1 - abs(polarity)) * 0.5  # Neutral component
        elif polarity < 0:
            pos_score = normalized_polarity  
            neg_score = 1 - normalized_polarity
            neu_score = (1 - abs(polarity)) * 0.5
        else:
            pos_score = 0.33
            neg_score = 0.33
            neu_score = 0.34
        
        # Normalize scores to sum to 1
        total = pos_score + neg_score + neu_score
        if total > 0:
            pos_score /= total
            neg_score /= total
            neu_score /= total
        
        sentiment_scores = {
            'positive': pos_score,
            'negative': neg_score,
            'neutral': neu_score
        }
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': sentiment_scores,
            'polarity': polarity,
            'subjectivity': subjectivity
        } 