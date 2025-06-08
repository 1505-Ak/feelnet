"""
VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analyzer.
Particularly good for social media text and informal language.
"""

from typing import Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..analyzers.sentiment_analyzer import SentimentLabel


class VaderAnalyzer:
    """
    VADER sentiment analyzer wrapper.
    
    VADER is specifically attuned to sentiments expressed in social media text.
    It performs well on texts from different domains.
    """
    
    def __init__(self):
        """Initialize VADER analyzer."""
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        # Get VADER scores
        scores = self.analyzer.polarity_scores(text)
        
        # VADER returns: neg, neu, pos, compound
        # compound score is the normalized, weighted composite score
        compound = scores['compound']
        
        # Determine sentiment based on compound score
        if compound >= 0.05:
            sentiment = SentimentLabel.POSITIVE
            confidence = scores['pos']
        elif compound <= -0.05:
            sentiment = SentimentLabel.NEGATIVE  
            confidence = scores['neg']
        else:
            sentiment = SentimentLabel.NEUTRAL
            confidence = scores['neu']
        
        # Normalize scores for consistency
        sentiment_scores = {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': sentiment_scores,
            'raw_scores': scores,
            'compound': compound
        } 