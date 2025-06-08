#!/usr/bin/env python3
"""
feelnet Demo Script

This script demonstrates the core functionality of the feelnet sentiment analysis tool.
Run this script to see examples of sentiment analysis in action.
"""

import os
import sys
import logging
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src import SentimentAnalyzer, ScraperFactory, TextPreprocessor
    from src.analyzers.sentiment_analyzer import SentimentResult
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_analysis():
    """Demonstrate basic sentiment analysis."""
    print("\n" + "="*60)
    print("🧠 FEELNET SENTIMENT ANALYSIS DEMO")
    print("="*60)
    
    # Sample texts for analysis
    sample_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is the worst purchase I've ever made. Completely disappointed.",
        "The item is okay, nothing special but does what it's supposed to do.",
        "Fantastic service! Highly recommend to everyone!",
        "Poor quality and terrible customer support. Avoid at all costs.",
        "It's an average product with some good and bad features.",
        "Incredible experience! Five stars all the way! ⭐⭐⭐⭐⭐",
        "Meh... could be better, could be worse. Just mediocre.",
        "Outstanding quality and fast delivery. Very satisfied!",
        "Broken on arrival. Waste of money. 😠"
    ]
    
    print(f"\n📝 Analyzing {len(sample_texts)} sample texts...\n")
    
    # Initialize analyzer with ensemble method
    analyzer = SentimentAnalyzer(method="ensemble")
    
    # Analyze each text
    results = []
    for i, text in enumerate(sample_texts, 1):
        print(f"Text {i}: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        try:
            result = analyzer.analyze(text)
            results.append(result)
            
            # Display result
            sentiment_color = {
                'positive': '🟢',
                'negative': '🔴', 
                'neutral': '🟡'
            }
            
            icon = sentiment_color.get(result.sentiment.value, '⚪')
            print(f"   {icon} Sentiment: {result.sentiment.value.upper()}")
            print(f"   📊 Confidence: {result.confidence:.3f}")
            print(f"   ⚡ Time: {result.processing_time:.3f}s")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            continue
    
    # Display statistics
    if results:
        stats = analyzer.get_statistics(results)
        print("📈 ANALYSIS STATISTICS")
        print("-" * 30)
        print(f"Total analyzed: {stats['total_analyzed']}")
        print(f"Average confidence: {stats['average_confidence']:.3f}")
        print(f"Total processing time: {stats['total_processing_time']:.3f}s")
        print(f"Average processing time: {stats['average_processing_time']:.3f}s")
        
        print("\n📊 Sentiment Distribution:")
        for sentiment, percentage in stats['sentiment_distribution'].items():
            bar_length = int(percentage * 20)  # Scale to 20 chars
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {sentiment.capitalize():8}: {bar} {percentage:.1%}")


def demo_different_methods():
    """Demonstrate different analysis methods."""
    print("\n" + "="*60)
    print("🔬 COMPARING ANALYSIS METHODS")
    print("="*60)
    
    test_text = "This movie is absolutely fantastic! The acting is superb and the story is captivating. Highly recommended!"
    
    methods = ['vader', 'textblob', 'transformer', 'ensemble']
    
    print(f"\n📝 Text: {test_text}\n")
    
    for method in methods:
        print(f"🔍 Method: {method.upper()}")
        try:
            analyzer = SentimentAnalyzer(method=method)
            result = analyzer.analyze(test_text)
            
            print(f"   Sentiment: {result.sentiment.value}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Scores: {result.scores}")
            print(f"   Time: {result.processing_time:.3f}s")
            print()
            
        except Exception as e:
            print(f"   ❌ Error with {method}: {e}\n")


def demo_preprocessing():
    """Demonstrate text preprocessing."""
    print("\n" + "="*60)
    print("🔧 TEXT PREPROCESSING DEMO")
    print("="*60)
    
    # Sample messy text
    messy_text = """
    <p>This is a GREAT product!!! 😍 
    Visit our website at https://example.com or email us at contact@example.com.
    
    The quality is amazing... I LOVE IT SO MUCH!!! 
    #BestPurchase #Recommended 💯</p>
    """
    
    print(f"📝 Original text:\n{messy_text}")
    
    # Different preprocessing configurations
    configs = [
        ("Basic cleaning", {"remove_urls": True, "remove_emails": True, "remove_html": True}),
        ("Lowercase + basic", {"remove_urls": True, "remove_emails": True, "remove_html": True, "lowercase": True}),
        ("Full preprocessing", {"remove_urls": True, "remove_emails": True, "remove_html": True, 
                              "lowercase": True, "remove_special_chars": True})
    ]
    
    for name, config in configs:
        print(f"\n🔧 {name}:")
        preprocessor = TextPreprocessor(**config)
        cleaned = preprocessor.preprocess(messy_text)
        print(f"   Result: {cleaned}")


def demo_scraper_info():
    """Demonstrate scraper information."""
    print("\n" + "="*60)
    print("🕷️ WEB SCRAPING CAPABILITIES")
    print("="*60)
    
    try:
        factory = ScraperFactory()
        info = factory.get_scraper_info()
        
        print(f"📊 Total scrapers available: {info['total_scrapers']}")
        print(f"🌐 Supported platforms: {', '.join(info['platforms'])}")
        print(f"🔗 Total supported domains: {len(info['supported_domains'])}")
        
        print("\n📋 Platform Details:")
        for platform, details in info['platform_details'].items():
            print(f"\n  🏢 {platform.upper()}:")
            if 'error' in details:
                print(f"     ❌ Error: {details['error']}")
            else:
                print(f"     📂 Class: {details['class_name']}")
                print(f"     🌐 Domains: {', '.join(details['supported_domains'])}")
        
        # Test URL validation
        test_urls = [
            "https://amazon.com/product/dp/B123456789",
            "https://www.imdb.com/title/tt1234567",
            "https://tripadvisor.com/Hotel_Review-123456",
            "https://unsupported-site.com/reviews"
        ]
        
        print("\n🔍 URL Support Test:")
        for url in test_urls:
            is_supported = factory.is_url_supported(url)
            status = "✅ Supported" if is_supported else "❌ Not supported"
            print(f"   {url}: {status}")
            
    except Exception as e:
        print(f"❌ Error testing scrapers: {e}")


def demo_batch_analysis():
    """Demonstrate batch analysis."""
    print("\n" + "="*60)
    print("⚡ BATCH ANALYSIS DEMO")
    print("="*60)
    
    # Sample customer reviews
    reviews = [
        "Fast shipping and excellent quality. Very pleased with this purchase!",
        "Product arrived damaged and customer service was unhelpful.",
        "Average product, nothing special but does the job.",
        "Exceeded my expectations! Will definitely buy again.",
        "Overpriced for what you get. Not worth the money.",
        "Good value for money. Solid build quality.",
        "Terrible experience. Product broke after one use.",
        "Perfect! Exactly what I was looking for.",
        "Okay product but shipping took forever.",
        "Love it! Highly recommend to others!"
    ]
    
    print(f"📦 Processing {len(reviews)} customer reviews...\n")
    
    try:
        analyzer = SentimentAnalyzer(method="ensemble")
        results = analyzer.analyze_batch(reviews)
        
        # Display results in a table-like format
        print("📊 BATCH ANALYSIS RESULTS")
        print("-" * 80)
        print(f"{'#':<3} {'Sentiment':<10} {'Confidence':<12} {'Review Preview':<50}")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            preview = result.text[:47] + "..." if len(result.text) > 50 else result.text
            sentiment_icon = {'positive': '🟢', 'negative': '🔴', 'neutral': '🟡'}
            icon = sentiment_icon.get(result.sentiment.value, '⚪')
            
            print(f"{i:<3} {icon} {result.sentiment.value:<8} {result.confidence:<11.3f} {preview}")
        
        # Statistics
        stats = analyzer.get_statistics(results)
        print("\n📈 BATCH STATISTICS")
        print("-" * 30)
        for sentiment, percentage in stats['sentiment_distribution'].items():
            print(f"{sentiment.capitalize()}: {percentage:.1%}")
        
        print(f"\nTotal processing time: {stats['total_processing_time']:.2f}s")
        print(f"Average time per review: {stats['average_processing_time']:.3f}s")
        
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")


def main():
    """Run all demonstrations."""
    print("🚀 Starting feelnet demonstration...")
    
    try:
        demo_basic_analysis()
        demo_different_methods()
        demo_preprocessing()
        demo_scraper_info()
        demo_batch_analysis()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n💡 Next steps:")
        print("   1. Try the web interface: python app.py")
        print("   2. Explore the API endpoints")
        print("   3. Customize the analyzers for your needs")
        print("   4. Build your own scrapers for new platforms")
        print("\n📚 Documentation: https://github.com/yourusername/feelnet")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo error")


if __name__ == "__main__":
    main() 