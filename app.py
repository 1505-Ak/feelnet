"""
Main Flask application for feelnet - Sentiment Analysis Tool.

Provides both web interface and REST API for sentiment analysis.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_cors import CORS
import sqlite3
from typing import Dict, List

# Import feelnet modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src import SentimentAnalyzer, ScraperFactory, TextPreprocessor
    from src.analyzers.sentiment_analyzer import SentimentResult
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'feelnet-secret-key-change-in-production')
CORS(app)

# Initialize feelnet components
analyzer = SentimentAnalyzer(method="ensemble")
scraper_factory = ScraperFactory()
preprocessor = TextPreprocessor()

# Database setup
DATABASE = 'data/feelnet.db'


def init_database():
    """Initialize SQLite database for storing analysis results."""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence REAL NOT NULL,
            scores TEXT NOT NULL,
            method TEXT NOT NULL,
            processing_time REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_url TEXT,
            platform TEXT
        )
    ''')
    
    # Create scraped reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraped_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            rating REAL,
            author TEXT,
            date TEXT,
            title TEXT,
            helpful_votes INTEGER,
            verified BOOLEAN,
            source_url TEXT NOT NULL,
            platform TEXT NOT NULL,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def save_analysis_result(result: SentimentResult, source_url: str = None, platform: str = None):
    """Save analysis result to database."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (text, sentiment, confidence, scores, method, processing_time, source_url, platform)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.text,
            result.sentiment.value,
            result.confidence,
            json.dumps(result.scores),
            result.method,
            result.processing_time,
            source_url,
            platform
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error saving analysis result: {e}")


# Web Routes
@app.route('/')
def index():
    """Main page with sentiment analysis interface."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analyze sentiment of submitted text."""
    try:
        text = request.form.get('text', '').strip()
        method = request.form.get('method', 'ensemble')
        
        if not text:
            flash('Please enter some text to analyze.', 'error')
            return redirect(url_for('index'))
        
        # Create analyzer with specified method
        temp_analyzer = SentimentAnalyzer(method=method)
        result = temp_analyzer.analyze(text)
        
        # Save result to database
        save_analysis_result(result)
        
        return render_template('result.html', result=result)
        
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        flash(f'Error analyzing text: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/scrape')
def scrape_reviews():
    """Scrape and analyze reviews from supported platforms."""
    supported_platforms = scraper_factory.get_supported_platforms()
    return render_template('scrape.html', platforms=supported_platforms)

@app.route('/scrape/submit', methods=['POST'])
def scrape_submit():
    """Process scraping form submission."""
    
    try:
        url = request.form.get('url', '').strip()
        max_reviews = int(request.form.get('max_reviews', 50))
        
        if not url:
            flash('Please enter a URL to scrape.', 'error')
            return redirect(url_for('scrape_reviews'))
        
        # Get appropriate scraper
        scraper = scraper_factory.get_scraper_by_url(url)
        if not scraper:
            flash('URL not supported. Please check supported platforms.', 'error')
            return redirect(url_for('scrape_reviews'))
        
        # Scrape reviews
        reviews = scraper.scrape_reviews(url, max_reviews=max_reviews)
        
        if not reviews:
            flash('No reviews found or unable to scrape from the provided URL.', 'warning')
            return redirect(url_for('scrape_reviews'))
        
        # Analyze sentiment of each review
        results = []
        for review in reviews:
            try:
                result = analyzer.analyze(review.text)
                save_analysis_result(result, source_url=url, platform=review.platform)
                
                results.append({
                    'review': review,
                    'sentiment': result
                })
            except Exception as e:
                logger.error(f"Error analyzing review: {e}")
                continue
        
        # Calculate statistics
        if results:
            stats = analyzer.get_statistics([r['sentiment'] for r in results])
            return render_template('scrape_results.html', 
                                 results=results, 
                                 stats=stats, 
                                 url=url)
        else:
            flash('Unable to analyze any reviews.', 'error')
            return redirect(url_for('scrape_reviews'))
            
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
        flash(f'Error scraping reviews: {str(e)}', 'error')
        return redirect(url_for('scrape_reviews'))


@app.route('/history')
def analysis_history():
    """View analysis history."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_history 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''')
        
        history = cursor.fetchall()
        conn.close()
        
        return render_template('history.html', history=history)
        
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        flash(f'Error loading history: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """Analytics dashboard."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get sentiment distribution
        cursor.execute('''
            SELECT sentiment, COUNT(*) as count 
            FROM analysis_history 
            GROUP BY sentiment
        ''')
        sentiment_dist = dict(cursor.fetchall())
        
        # Get analysis by method
        cursor.execute('''
            SELECT method, COUNT(*) as count 
            FROM analysis_history 
            GROUP BY method
        ''')
        method_dist = dict(cursor.fetchall())
        
        # Get recent activity
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM analysis_history 
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''')
        activity = cursor.fetchall()
        
        conn.close()
        
        # Calculate stats for template
        total_analyses = sum(sentiment_dist.values()) if sentiment_dist else 0
        stats = {
            'total_analyses': total_analyses,
            'positive_count': sentiment_dist.get('positive', 0),
            'negative_count': sentiment_dist.get('negative', 0),
            'neutral_count': sentiment_dist.get('neutral', 0),
            'avg_confidence': 0.65,  # Placeholder
            'most_common': max(sentiment_dist, key=sentiment_dist.get) if sentiment_dist else 'neutral',
            'this_week_count': total_analyses  # Placeholder
        }
        
        return render_template('dashboard.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))


# API Routes
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for sentiment analysis."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        method = data.get('method', 'ensemble')
        
        # Create analyzer with specified method
        temp_analyzer = SentimentAnalyzer(method=method)
        result = temp_analyzer.analyze(text)
        
        # Save result
        save_analysis_result(result)
        
        return jsonify({
            'text': result.text,
            'sentiment': result.sentiment.value,
            'confidence': result.confidence,
            'scores': result.scores,
            'method': result.method,
            'processing_time': result.processing_time
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/batch', methods=['POST'])
def api_analyze_batch():
    """API endpoint for batch sentiment analysis."""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'Texts array is required'}), 400
        
        texts = data['texts']
        method = data.get('method', 'ensemble')
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be an array'}), 400
        
        # Create analyzer
        temp_analyzer = SentimentAnalyzer(method=method)
        results = temp_analyzer.analyze_batch(texts)
        
        # Save results
        for result in results:
            save_analysis_result(result)
        
        # Format response
        response_data = []
        for result in results:
            response_data.append({
                'text': result.text,
                'sentiment': result.sentiment.value,
                'confidence': result.confidence,
                'scores': result.scores,
                'processing_time': result.processing_time
            })
        
        # Include statistics
        stats = temp_analyzer.get_statistics(results)
        
        return jsonify({
            'results': response_data,
            'statistics': stats,
            'method': method
        })
        
    except Exception as e:
        logger.error(f"API batch error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint for scraping and analyzing reviews."""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        max_reviews = data.get('max_reviews', 50)
        
        # Get appropriate scraper
        scraper = scraper_factory.get_scraper_by_url(url)
        if not scraper:
            return jsonify({'error': 'URL not supported'}), 400
        
        # Scrape reviews
        reviews = scraper.scrape_reviews(url, max_reviews=max_reviews)
        
        if not reviews:
            return jsonify({'error': 'No reviews found'}), 404
        
        # Analyze sentiment
        results = []
        for review in reviews:
            try:
                result = analyzer.analyze(review.text)
                save_analysis_result(result, source_url=url, platform=review.platform)
                
                results.append({
                    'review': {
                        'text': review.text,
                        'rating': review.rating,
                        'author': review.author,
                        'date': review.date,
                        'title': review.title,
                        'platform': review.platform
                    },
                    'sentiment': {
                        'sentiment': result.sentiment.value,
                        'confidence': result.confidence,
                        'scores': result.scores
                    }
                })
            except Exception as e:
                logger.error(f"Error analyzing review: {e}")
                continue
        
        # Calculate statistics
        sentiment_results = [analyzer.analyze(r.text) for r in reviews]
        stats = analyzer.get_statistics(sentiment_results)
        
        return jsonify({
            'url': url,
            'total_reviews': len(reviews),
            'analyzed_reviews': len(results),
            'results': results,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"API scrape error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/platforms')
def api_platforms():
    """API endpoint to get supported platforms."""
    try:
        platforms = scraper_factory.get_supported_platforms()
        info = scraper_factory.get_scraper_info()
        
        return jsonify({
            'supported_platforms': platforms,
            'scraper_info': info
        })
        
    except Exception as e:
        logger.error(f"API platforms error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def api_health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting feelnet server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 