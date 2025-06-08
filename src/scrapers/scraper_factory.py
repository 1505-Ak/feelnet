"""
Factory class for creating appropriate scrapers based on platform or URL.
"""

from typing import Dict, Type, Optional
from urllib.parse import urlparse
import logging

from .base_scraper import BaseScraper
from .amazon_scraper import AmazonScraper
from .imdb_scraper import IMDbScraper
from .tripadvisor_scraper import TripAdvisorScraper

logger = logging.getLogger(__name__)


class ScraperFactory:
    """
    Factory class for creating platform-specific scrapers.
    
    Automatically selects the appropriate scraper based on URL domain
    or platform name.
    """
    
    def __init__(self):
        """Initialize scraper factory with available scrapers."""
        self._scrapers: Dict[str, Type[BaseScraper]] = {
            'amazon': AmazonScraper,
            'imdb': IMDbScraper,
            'tripadvisor': TripAdvisorScraper
        }
        
        # Domain to scraper mapping
        self._domain_mapping = {}
        self._build_domain_mapping()
    
    def _build_domain_mapping(self):
        """Build mapping from domains to scrapers."""
        for platform, scraper_class in self._scrapers.items():
            try:
                # Create temporary instance to get supported domains
                temp_scraper = scraper_class()
                domains = temp_scraper.get_supported_domains()
                
                for domain in domains:
                    self._domain_mapping[domain.lower()] = scraper_class
                    
            except Exception as e:
                logger.warning(f"Error setting up {platform} scraper: {e}")
    
    def get_scraper_by_url(self, url: str, **kwargs) -> Optional[BaseScraper]:
        """
        Get appropriate scraper for a given URL.
        
        Args:
            url: URL to scrape
            **kwargs: Arguments to pass to scraper constructor
            
        Returns:
            Appropriate scraper instance or None if not supported
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check direct domain match
            if domain in self._domain_mapping:
                scraper_class = self._domain_mapping[domain]
                return scraper_class(**kwargs)
            
            # Check if domain contains any supported domain
            for supported_domain, scraper_class in self._domain_mapping.items():
                if supported_domain in domain:
                    return scraper_class(**kwargs)
            
            logger.warning(f"No scraper found for domain: {domain}")
            return None
            
        except Exception as e:
            logger.error(f"Error determining scraper for URL {url}: {e}")
            return None
    
    def get_scraper_by_platform(self, platform: str, **kwargs) -> Optional[BaseScraper]:
        """
        Get scraper for specific platform.
        
        Args:
            platform: Platform name (e.g., 'amazon', 'imdb', 'tripadvisor')
            **kwargs: Arguments to pass to scraper constructor
            
        Returns:
            Scraper instance or None if platform not supported
        """
        platform_lower = platform.lower()
        
        if platform_lower in self._scrapers:
            scraper_class = self._scrapers[platform_lower]
            return scraper_class(**kwargs)
        
        logger.warning(f"Platform '{platform}' not supported")
        return None
    
    def get_supported_platforms(self) -> Dict[str, list]:
        """
        Get list of supported platforms and their domains.
        
        Returns:
            Dictionary mapping platform names to supported domains
        """
        result = {}
        
        for platform, scraper_class in self._scrapers.items():
            try:
                temp_scraper = scraper_class()
                result[platform] = temp_scraper.get_supported_domains()
            except Exception as e:
                logger.warning(f"Error getting domains for {platform}: {e}")
                result[platform] = []
        
        return result
    
    def is_url_supported(self, url: str) -> bool:
        """
        Check if URL is supported by any scraper.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is supported
        """
        scraper = self.get_scraper_by_url(url)
        return scraper is not None
    
    def register_scraper(self, platform: str, scraper_class: Type[BaseScraper]):
        """
        Register a new scraper for a platform.
        
        Args:
            platform: Platform name
            scraper_class: Scraper class to register
        """
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError("Scraper class must inherit from BaseScraper")
        
        self._scrapers[platform.lower()] = scraper_class
        
        # Update domain mapping
        try:
            temp_scraper = scraper_class()
            domains = temp_scraper.get_supported_domains()
            
            for domain in domains:
                self._domain_mapping[domain.lower()] = scraper_class
                
        except Exception as e:
            logger.warning(f"Error registering scraper for {platform}: {e}")
        
        logger.info(f"Registered scraper for platform: {platform}")
    
    def get_scraper_info(self) -> Dict:
        """
        Get information about all available scrapers.
        
        Returns:
            Dictionary with scraper information
        """
        info = {
            'total_scrapers': len(self._scrapers),
            'platforms': list(self._scrapers.keys()),
            'supported_domains': list(self._domain_mapping.keys()),
            'platform_details': {}
        }
        
        for platform, scraper_class in self._scrapers.items():
            try:
                temp_scraper = scraper_class()
                info['platform_details'][platform] = {
                    'class_name': scraper_class.__name__,
                    'supported_domains': temp_scraper.get_supported_domains(),
                    'platform_name': temp_scraper.get_platform_name()
                }
            except Exception as e:
                logger.warning(f"Error getting info for {platform}: {e}")
                info['platform_details'][platform] = {
                    'class_name': scraper_class.__name__,
                    'error': str(e)
                }
        
        return info 