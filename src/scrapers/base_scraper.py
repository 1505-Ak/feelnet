"""
Base scraper class providing common functionality for all platform scrapers.
"""

import time
import random
import requests
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class ReviewData:
    """Container for scraped review data."""
    text: str
    rating: Optional[float]
    author: Optional[str]
    date: Optional[str]
    title: Optional[str]
    helpful_votes: Optional[int]
    verified: bool
    source_url: str
    platform: str


class BaseScraper(ABC):
    """
    Base class for all platform scrapers.
    
    Provides common functionality including rate limiting, request management,
    and error handling.
    """
    
    def __init__(self, 
                 rate_limit: float = 1.0,
                 timeout: int = 30,
                 retries: int = 3,
                 user_agent: str = None):
        """
        Initialize base scraper.
        
        Args:
            rate_limit: Minimum time between requests (seconds)
            timeout: Request timeout (seconds)
            retries: Number of retry attempts
            user_agent: Custom user agent string
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retries = retries
        self.last_request_time = 0
        
        # Setup session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or self._get_default_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _get_default_user_agent(self) -> str:
        """Get default user agent string."""
        return ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36')
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting and error handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    url, 
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    logger.warning(f"Rate limited. Waiting before retry...")
                    time.sleep(random.uniform(5, 10))
                    continue
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < self.retries - 1:
                    time.sleep(random.uniform(1, 3))
                    continue
        
        return None
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @abstractmethod
    def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[ReviewData]:
        """
        Scrape reviews from a specific URL.
        
        Args:
            url: URL to scrape reviews from
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of ReviewData objects
        """
        pass
    
    @abstractmethod
    def search_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products/items on the platform.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of product/item information dictionaries
        """
        pass
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL belongs to this platform.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid for this platform
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() in self.get_supported_domains()
        except:
            return False
    
    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported domain names for this scraper.
        
        Returns:
            List of domain names
        """
        pass
    
    def get_platform_name(self) -> str:
        """Get the platform name for this scraper."""
        return self.__class__.__name__.replace('Scraper', '')
    
    def _extract_text(self, element) -> str:
        """
        Extract clean text from BeautifulSoup element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Cleaned text string
        """
        if element is None:
            return ""
        
        text = element.get_text(strip=True)
        # Clean up common HTML entities and extra whitespace
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())  # Normalize whitespace
        return text
    
    def _safe_float_convert(self, value: str) -> Optional[float]:
        """
        Safely convert string to float.
        
        Args:
            value: String value to convert
            
        Returns:
            Float value or None if conversion fails
        """
        if not value:
            return None
        
        try:
            # Remove common non-numeric characters
            cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int_convert(self, value: str) -> Optional[int]:
        """
        Safely convert string to int.
        
        Args:
            value: String value to convert
            
        Returns:
            Integer value or None if conversion fails
        """
        if not value:
            return None
        
        try:
            # Remove common non-numeric characters
            cleaned = ''.join(c for c in str(value) if c.isdigit())
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None 