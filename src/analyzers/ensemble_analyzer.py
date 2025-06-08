"""
Ensemble analyzer that combines multiple sentiment analysis methods.
"""

from typing import Dict, List
import logging

from .vader_analyzer import VaderAnalyzer
from .textblob_analyzer import TextBlobAnalyzer
from .transformer_analyzer import TransformerAnalyzer
from enum import Enum

class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

logger = logging.getLogger(__name__)


class EnsembleAnalyzer:
    """
    Ensemble sentiment analyzer that combines multiple methods for improved accuracy.
    
    Uses weighted voting from VADER, TextBlob, and Transformer models.
    """
    
    def __init__(self, 
                 use_vader: bool = True,
                 use_textblob: bool = True,
                 use_transformer: bool = True,
                 vader_weight: float = 0.4,
                 textblob_weight: float = 0.3,
                 transformer_weight: float = 0.3):
        """
        Initialize ensemble analyzer.
        
        Args:
            use_vader: Whether to include VADER analyzer
            use_textblob: Whether to include TextBlob analyzer
            use_transformer: Whether to include Transformer analyzer
            vader_weight: Weight for VADER results
            textblob_weight: Weight for TextBlob results
            transformer_weight: Weight for Transformer results
        """
        self.analyzers = {}
        self.weights = {}
        
        if use_vader:
            self.analyzers['vader'] = VaderAnalyzer()
            self.weights['vader'] = vader_weight
            
        if use_textblob:
            self.analyzers['textblob'] = TextBlobAnalyzer()
            self.weights['textblob'] = textblob_weight
            
        if use_transformer:
            self.analyzers['transformer'] = TransformerAnalyzer()
            self.weights['transformer'] = transformer_weight
        
        # Normalize weights
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
        logger.info(f"Ensemble analyzer initialized with {len(self.analyzers)} methods")
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment using ensemble of methods.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing ensemble results
        """
        if not self.analyzers:
            raise ValueError("No analyzers configured")
        
        individual_results = {}
        combined_scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        # Get results from each analyzer
        for name, analyzer in self.analyzers.items():
            try:
                result = analyzer.analyze(text)
                individual_results[name] = result
                
                # Combine scores using weights
                weight = self.weights.get(name, 0.0)
                for sentiment, score in result['scores'].items():
                    combined_scores[sentiment] += score * weight
                    
            except Exception as e:
                logger.warning(f"Error in {name} analyzer: {e}")
                continue
        
        # Normalize combined scores
        total = sum(combined_scores.values())
        if total > 0:
            combined_scores = {k: v / total for k, v in combined_scores.items()}
        
        # Determine final sentiment
        final_sentiment = max(combined_scores, key=combined_scores.get)
        confidence = combined_scores[final_sentiment]
        
        return {
            'sentiment': SentimentLabel(final_sentiment),
            'confidence': confidence,
            'scores': combined_scores,
            'individual_results': individual_results,
            'method': 'ensemble'
        }
    
    def get_analyzer_performance(self, texts: List[str]) -> Dict:
        """
        Analyze performance of individual analyzers on a set of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Performance metrics for each analyzer
        """
        performance = {}
        
        for name, analyzer in self.analyzers.items():
            try:
                results = []
                for text in texts:
                    result = analyzer.analyze(text)
                    results.append(result)
                
                # Calculate metrics
                confidences = [r['confidence'] for r in results]
                avg_confidence = sum(confidences) / len(confidences)
                
                sentiments = [r['sentiment'].value for r in results]
                sentiment_dist = {
                    'positive': sentiments.count('positive') / len(sentiments),
                    'negative': sentiments.count('negative') / len(sentiments),
                    'neutral': sentiments.count('neutral') / len(sentiments)
                }
                
                performance[name] = {
                    'average_confidence': avg_confidence,
                    'sentiment_distribution': sentiment_dist,
                    'total_analyzed': len(results)
                }
                
            except Exception as e:
                logger.error(f"Error analyzing performance for {name}: {e}")
                performance[name] = {'error': str(e)}
        
        return performance 