"""
Transformer-based sentiment analyzer using pre-trained models.
Provides state-of-the-art accuracy for sentiment classification.
"""

import os
os.environ.setdefault("TRANSFORMERS_NO_TF","1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX","1")

from typing import Dict, Optional
import logging
from enum import Enum

class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

logger = logging.getLogger(__name__)


class TransformerAnalyzer:
    """
    Transformer-based sentiment analyzer using Hugging Face models.
    
    Uses pre-trained transformer models for high-accuracy sentiment analysis.
    Default model is optimized for English text sentiment classification.
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize transformer analyzer.
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model_name = model_name
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the transformer model pipeline."""
        try:
            from transformers import pipeline  # lazy import
            logger.info(f"Loading transformer model: {self.model_name}")
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True
            )
            logger.info("Transformer model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading transformer model: {e}")
            # Fallback to a simpler model
            try:
                logger.info("Trying fallback model...")
                self.pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    return_all_scores=True
                )
                logger.info("Fallback model loaded successfully")
            except Exception as e2:
                logger.error(f"Error loading fallback model: {e2}")
                self.pipeline = None
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using transformer model.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        if not self.pipeline:
            # Fallback to simple rule-based approach if model failed to load
            return self._fallback_analysis(text)
        
        try:
            # Truncate text if too long (transformer models have token limits)
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            # Get predictions
            results = self.pipeline(text)[0]  # Get first (and only) result
            
            # Parse results based on model type
            sentiment_scores = self._parse_results(results)
            
            # Determine primary sentiment
            primary_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            confidence = sentiment_scores[primary_sentiment]
            
            return {
                'sentiment': SentimentLabel(primary_sentiment),
                'confidence': confidence,
                'scores': sentiment_scores,
                'raw_results': results
            }
            
        except Exception as e:
            logger.error(f"Error in transformer analysis: {e}")
            return self._fallback_analysis(text)
    
    def _parse_results(self, results) -> Dict[str, float]:
        """
        Parse transformer model results into standard format.
        
        Args:
            results: Raw results from transformer pipeline
            
        Returns:
            Dictionary with normalized sentiment scores
        """
        sentiment_scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        for result in results:
            label = result['label'].lower()
            score = result['score']
            
            # Map various label formats to standard labels
            if 'pos' in label or label == 'label_2':
                sentiment_scores['positive'] = score
            elif 'neg' in label or label == 'label_0':
                sentiment_scores['negative'] = score
            elif 'neu' in label or label == 'label_1':
                sentiment_scores['neutral'] = score
            elif label == 'positive':
                sentiment_scores['positive'] = score
            elif label == 'negative':
                sentiment_scores['negative'] = score
            elif label == 'neutral':
                sentiment_scores['neutral'] = score
        
        # If no neutral score, distribute between positive and negative
        if sentiment_scores['neutral'] == 0.0:
            total = sentiment_scores['positive'] + sentiment_scores['negative']
            if total > 0:
                # Add small neutral component
                neutral_component = 0.1
                sentiment_scores['positive'] *= (1 - neutral_component)
                sentiment_scores['negative'] *= (1 - neutral_component)
                sentiment_scores['neutral'] = neutral_component
        
        return sentiment_scores
    
    def _fallback_analysis(self, text: str) -> Dict:
        """
        Fallback analysis when transformer model is not available.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with basic sentiment analysis
        """
        # Simple keyword-based approach as fallback
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 
                         'fantastic', 'love', 'like', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 
                         'worst', 'poor', 'disappointing', 'sad', 'angry']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if pos_count > neg_count:
            sentiment = SentimentLabel.POSITIVE
            confidence = min(0.8, pos_count / max(total_words * 0.1, 1))
        elif neg_count > pos_count:
            sentiment = SentimentLabel.NEGATIVE
            confidence = min(0.8, neg_count / max(total_words * 0.1, 1))
        else:
            sentiment = SentimentLabel.NEUTRAL
            confidence = 0.6
        
        # Create score distribution
        if sentiment == SentimentLabel.POSITIVE:
            scores = {'positive': confidence, 'negative': (1-confidence)*0.3, 'neutral': (1-confidence)*0.7}
        elif sentiment == SentimentLabel.NEGATIVE:
            scores = {'positive': (1-confidence)*0.3, 'negative': confidence, 'neutral': (1-confidence)*0.7}
        else:
            scores = {'positive': 0.3, 'negative': 0.3, 'neutral': 0.4}
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': scores,
            'fallback': True
        } 