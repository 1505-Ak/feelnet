"""
feelnet: A Sentiment Analysis Tool for Public Opinion Mining

This package provides comprehensive sentiment analysis capabilities for 
analyzing public opinions from online reviews and survey responses.
"""

from .analyzers.sentiment_analyzer import SentimentAnalyzer
from .analyzers.ensemble_analyzer import EnsembleAnalyzer
from .scrapers.scraper_factory import ScraperFactory
from .preprocessing.text_preprocessor import TextPreprocessor

__version__ = "1.0.0"
__author__ = "feelnet Team"
__email__ = "team@feelnet.com"

__all__ = [
    "SentimentAnalyzer",
    "EnsembleAnalyzer", 
    "ScraperFactory",
    "TextPreprocessor"
] 