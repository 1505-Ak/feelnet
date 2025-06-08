#!/usr/bin/env python3
"""
feelnet Setup Script

This script helps set up the feelnet development environment.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_command(command, description):
    """Run a shell command and handle errors."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        if e.stderr:
            logger.error(e.stderr.strip())
        return False


def check_python_version():
    """Check if Python version is compatible."""
    logger.info("Checking Python version...")
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python {sys.version_info.major}.{sys.version_info.minor} - OK")
    return True


def install_dependencies():
    """Install required dependencies."""
    logger.info("Installing dependencies...")
    
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing Python packages"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def download_nltk_data():
    """Download required NLTK data."""
    logger.info("Downloading NLTK data...")
    
    try:
        import nltk
        
        # Download essential NLTK data
        datasets = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon']
        
        for dataset in datasets:
            try:
                nltk.download(dataset, quiet=True)
                logger.info(f"Downloaded NLTK dataset: {dataset}")
            except Exception as e:
                logger.warning(f"Failed to download {dataset}: {e}")
        
        return True
        
    except ImportError:
        logger.error("NLTK not installed. Please install dependencies first.")
        return False


def create_directories():
    """Create necessary directories."""
    logger.info("Creating directories...")
    
    directories = [
        'data',
        'logs',
        'models',
        'temp'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    return True


def create_config_file():
    """Create configuration file from example."""
    logger.info("Setting up configuration...")
    
    if not os.path.exists('.env'):
        if os.path.exists('config.env.example'):
            try:
                with open('config.env.example', 'r') as src:
                    content = src.read()
                
                with open('.env', 'w') as dst:
                    dst.write(content)
                
                logger.info("Created .env file from example")
            except Exception as e:
                logger.error(f"Failed to create .env file: {e}")
                return False
        else:
            logger.warning("No config example found, skipping .env creation")
    else:
        logger.info(".env file already exists")
    
    return True


def run_tests():
    """Run installation tests."""
    logger.info("Running installation tests...")
    
    try:
        result = subprocess.run([sys.executable, 'test_installation.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("All tests passed!")
            return True
        else:
            logger.error("Some tests failed:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")
        return False


def main():
    """Main setup function."""
    print("🧠 feelnet Setup Script")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Downloading NLTK data", download_nltk_data),
        ("Creating directories", create_directories),
        ("Setting up configuration", create_config_file),
        ("Running tests", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n📋 {step_name}...")
        if not step_function():
            failed_steps.append(step_name)
            logger.error(f"Step failed: {step_name}")
    
    print("\n" + "=" * 40)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run demo: python demo.py")
        print("   2. Start web app: python app.py")
        print("   3. Test API: curl http://localhost:5000/api/health")
        print("\n📚 Documentation: README.md")
        return True
    else:
        print(f"❌ Setup failed. Failed steps: {', '.join(failed_steps)}")
        print("\n🔧 Try fixing the errors above and run setup again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 