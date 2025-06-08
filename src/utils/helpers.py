"""
Helper utility functions for feelnet.
"""

import re
from typing import Dict, Any, Optional


def format_confidence(confidence: float) -> str:
    """Format confidence score as percentage string."""
    return f"{confidence * 100:.1f}%"


def get_sentiment_color(sentiment: str) -> str:
    """Get color code for sentiment visualization."""
    colors = {
        'positive': '#27ae60',  # Green
        'negative': '#e74c3c',  # Red
        'neutral': '#f39c12'    # Orange
    }
    return colors.get(sentiment.lower(), '#6c757d')


def validate_text_input(text: str, max_length: int = 10000) -> Dict[str, Any]:
    """Validate text input for analysis."""
    if not text or not isinstance(text, str):
        return {'valid': False, 'error': 'Text is required'}
    
    text = text.strip()
    if len(text) == 0:
        return {'valid': False, 'error': 'Text cannot be empty'}
    if len(text) > max_length:
        return {'valid': False, 'error': f'Text too long. Max {max_length} chars'}
    
    return {'valid': True, 'cleaned_text': text, 'length': len(text)} 