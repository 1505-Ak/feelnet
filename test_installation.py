#!/usr/bin/env python3
"""
feelnet Installation Test

Quick test to verify that feelnet is properly installed and working.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test core imports
        from src.analyzers.sentiment_analyzer import SentimentAnalyzer, SentimentLabel
        from src.analyzers.vader_analyzer import VaderAnalyzer
        from src.analyzers.textblob_analyzer import TextBlobAnalyzer
        from src.preprocessing.text_preprocessor import TextPreprocessor
        from src.scrapers.scraper_factory import ScraperFactory
        
        print("✅ All core modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available."""
    print("\n🔍 Testing dependencies...")
    
    dependencies = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'), 
        ('sklearn', 'scikit-learn'),
        ('vaderSentiment', 'vaderSentiment'),
        ('textblob', 'textblob'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('flask', 'flask')
    ]
    
    missing = []
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies available")
    return True

def test_basic_functionality():
    """Test basic sentiment analysis functionality."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.analyzers.sentiment_analyzer import SentimentAnalyzer
        
        # Test VADER analyzer (most reliable)
        analyzer = SentimentAnalyzer(method="vader")
        
        test_texts = [
            "I love this product!",
            "This is terrible.",
            "It's okay, nothing special."
        ]
        
        for text in test_texts:
            result = analyzer.analyze(text)
            print(f"✅ '{text}' → {result.sentiment.value} ({result.confidence:.2f})")
        
        print("✅ Basic sentiment analysis working")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_preprocessor():
    """Test text preprocessing."""
    print("\n🔍 Testing text preprocessor...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.preprocessing.text_preprocessor import TextPreprocessor
        
        preprocessor = TextPreprocessor()
        test_text = "<p>Visit https://example.com for more info!</p>"
        cleaned = preprocessor.preprocess(test_text)
        
        print(f"✅ Original: {test_text}")
        print(f"✅ Cleaned: {cleaned}")
        print("✅ Text preprocessing working")
        return True
        
    except Exception as e:
        print(f"❌ Preprocessor test failed: {e}")
        return False

def test_scraper_factory():
    """Test scraper factory."""
    print("\n🔍 Testing scraper factory...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from src.scrapers.scraper_factory import ScraperFactory
        
        factory = ScraperFactory()
        platforms = factory.get_supported_platforms()
        
        print(f"✅ Supported platforms: {list(platforms.keys())}")
        
        # Test URL validation
        test_url = "https://amazon.com/product/test"
        is_supported = factory.is_url_supported(test_url)
        print(f"✅ URL validation working: {test_url} → {is_supported}")
        
        print("✅ Scraper factory working")
        return True
        
    except Exception as e:
        print(f"❌ Scraper factory test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧠 feelnet Installation Test")
    print("=" * 40)
    
    tests = [
        test_dependencies,
        test_imports,
        test_basic_functionality,
        test_preprocessor,
        test_scraper_factory
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! feelnet is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Run demo: python demo.py")
        print("   2. Start web app: python app.py")
        print("   3. Check API: curl http://localhost:5000/api/health")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Download NLTK data: python -c \"import nltk; nltk.download('all')\"")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 