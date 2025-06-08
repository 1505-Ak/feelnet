"""
Main sentiment analyzer class that provides a unified interface 
for different sentiment analysis approaches.
"""

from typing import Dict, List, Union, Optional
import logging
from dataclasses import dataclass
from enum import Enum

from .vader_analyzer import VaderAnalyzer
from .textblob_analyzer import TextBlobAnalyzer
from .transformer_analyzer import TransformerAnalyzer
from ..preprocessing.text_preprocessor import TextPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Container for sentiment analysis results."""
    text: str
    sentiment: SentimentLabel
    confidence: float
    scores: Dict[str, float]
    method: str
    processing_time: float


class SentimentAnalyzer:
    """
    Main sentiment analyzer class that provides multiple analysis methods
    and a unified interface for sentiment classification.
    """
    
    def __init__(self, method: str = "ensemble", preprocess: bool = True):
        """
        Initialize the sentiment analyzer.
        
        Args:
            method: Analysis method ('vader', 'textblob', 'transformer', 'ensemble')
            preprocess: Whether to preprocess text before analysis
        """
        self.method = method
        self.preprocess = preprocess
        self.preprocessor = TextPreprocessor() if preprocess else None
        
        # Initialize analyzers
        self.analyzers = {
            'vader': VaderAnalyzer(),
            'textblob': TextBlobAnalyzer(),
            'transformer': TransformerAnalyzer()
        }
        
        logger.info(f"SentimentAnalyzer initialized with method: {method}")
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            SentimentResult containing analysis results
        """
        import time
        start_time = time.time()
        
        # Preprocess text if enabled
        processed_text = text
        if self.preprocess and self.preprocessor:
            processed_text = self.preprocessor.preprocess(text)
        
        # Perform analysis based on selected method
        if self.method == "ensemble":
            result = self._ensemble_analyze(processed_text)
        else:
            analyzer = self.analyzers.get(self.method)
            if not analyzer:
                raise ValueError(f"Unknown analysis method: {self.method}")
            result = analyzer.analyze(processed_text)
        
        processing_time = time.time() - start_time
        
        return SentimentResult(
            text=text,
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            scores=result['scores'],
            method=self.method,
            processing_time=processing_time
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment of multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of SentimentResult objects
        """
        results = []
        logger.info(f"Analyzing batch of {len(texts)} texts")
        
        for i, text in enumerate(texts):
            try:
                result = self.analyze(text)
                results.append(result)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                logger.error(f"Error analyzing text {i}: {e}")
                # Create error result
                results.append(SentimentResult(
                    text=text,
                    sentiment=SentimentLabel.NEUTRAL,
                    confidence=0.0,
                    scores={'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
                    method=self.method,
                    processing_time=0.0
                ))
        
        return results
    
    def _ensemble_analyze(self, text: str) -> Dict:
        """
        Perform ensemble analysis using multiple methods.
        
        Args:
            text: Preprocessed text to analyze
            
        Returns:
            Dictionary with combined results
        """
        results = {}
        scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        # Get results from all analyzers
        for name, analyzer in self.analyzers.items():
            try:
                result = analyzer.analyze(text)
                results[name] = result
                
                # Aggregate scores (weighted average)
                weight = self._get_analyzer_weight(name)
                for sentiment, score in result['scores'].items():
                    scores[sentiment] += score * weight
                    
            except Exception as e:
                logger.warning(f"Error in {name} analyzer: {e}")
                continue
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        # Determine final sentiment
        sentiment_label = max(scores, key=scores.get)
        confidence = scores[sentiment_label]
        
        return {
            'sentiment': SentimentLabel(sentiment_label),
            'confidence': confidence,
            'scores': scores,
            'individual_results': results
        }
    
    def _get_analyzer_weight(self, analyzer_name: str) -> float:
        """Get weight for each analyzer in ensemble."""
        weights = {
            'vader': 0.4,      # Good for social media text
            'textblob': 0.3,   # Good for general text
            'transformer': 0.3  # Most accurate but slower
        }
        return weights.get(analyzer_name, 0.33)
    
    def get_statistics(self, results: List[SentimentResult]) -> Dict:
        """
        Calculate statistics from a batch of results.
        
        Args:
            results: List of sentiment analysis results
            
        Returns:
            Dictionary containing various statistics
        """
        if not results:
            return {}
        
        sentiments = [r.sentiment.value for r in results]
        confidences = [r.confidence for r in results]
        processing_times = [r.processing_time for r in results]
        
        stats = {
            'total_analyzed': len(results),
            'sentiment_distribution': {
                'positive': sentiments.count('positive') / len(sentiments),
                'negative': sentiments.count('negative') / len(sentiments),
                'neutral': sentiments.count('neutral') / len(sentiments)
            },
            'average_confidence': sum(confidences) / len(confidences),
            'total_processing_time': sum(processing_times),
            'average_processing_time': sum(processing_times) / len(processing_times)
        }
        
        return stats 