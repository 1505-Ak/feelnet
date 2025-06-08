"""
Amazon scraper for extracting product reviews.
"""

import re
from typing import List, Dict
from bs4 import BeautifulSoup
import logging

from .base_scraper import BaseScraper, ReviewData

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """
    Amazon product reviews scraper.
    
    Extracts reviews from Amazon product pages.
    Note: Amazon has strong anti-scraping measures, so this is for educational purposes.
    """
    
    def get_supported_domains(self) -> List[str]:
        """Get supported Amazon domains."""
        return [
            'amazon.com',
            'amazon.co.uk', 
            'amazon.ca',
            'amazon.de',
            'amazon.fr',
            'amazon.it',
            'amazon.es',
            'amazon.in',
            'amazon.com.au'
        ]
    
    def scrape_reviews(self, url: str, max_reviews: int = 100) -> List[ReviewData]:
        """
        Scrape reviews from Amazon product page.
        
        Args:
            url: Amazon product URL
            max_reviews: Maximum number of reviews to scrape
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        
        try:
            # First, try to get the reviews page URL
            reviews_url = self._get_reviews_url(url)
            if not reviews_url:
                logger.warning("Could not find reviews URL")
                return reviews
            
            page = 1
            while len(reviews) < max_reviews and page <= 10:  # Limit to 10 pages
                page_url = f"{reviews_url}&pageNumber={page}"
                
                response = self._make_request(page_url)
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_reviews = self._extract_reviews_from_page(soup, url)
                
                if not page_reviews:
                    break
                
                reviews.extend(page_reviews)
                page += 1
                
                if len(page_reviews) < 10:  # Less than full page, probably last page
                    break
            
            return reviews[:max_reviews]
            
        except Exception as e:
            logger.error(f"Error scraping Amazon reviews: {e}")
            return reviews
    
    def _get_reviews_url(self, product_url: str) -> str:
        """
        Get the reviews page URL from product URL.
        
        Args:
            product_url: Amazon product URL
            
        Returns:
            Reviews page URL
        """
        try:
            response = self._make_request(product_url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for reviews link
            reviews_link = soup.find('a', {'data-hook': 'see-all-reviews-link-foot'})
            if reviews_link and reviews_link.get('href'):
                return 'https://amazon.com' + reviews_link['href']
            
            # Alternative method - construct URL from ASIN
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            if asin_match:
                asin = asin_match.group(1)
                return f"https://amazon.com/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting reviews URL: {e}")
            return None
    
    def _extract_reviews_from_page(self, soup: BeautifulSoup, source_url: str) -> List[ReviewData]:
        """
        Extract reviews from a reviews page.
        
        Args:
            soup: BeautifulSoup object of the page
            source_url: Source URL for reference
            
        Returns:
            List of ReviewData objects
        """
        reviews = []
        
        # Find review containers
        review_containers = soup.find_all('div', {'data-hook': 'review'})
        
        for container in review_containers:
            try:
                review = self._extract_single_review(container, source_url)
                if review:
                    reviews.append(review)
            except Exception as e:
                logger.error(f"Error extracting single review: {e}")
                continue
        
        return reviews
    
    def _extract_single_review(self, container, source_url: str) -> ReviewData:
        """
        Extract a single review from its container.
        
        Args:
            container: BeautifulSoup element containing the review
            source_url: Source URL
            
        Returns:
            ReviewData object or None
        """
        try:
            # Extract text
            text_element = container.find('span', {'data-hook': 'review-body'})
            if not text_element:
                return None
            
            text = self._extract_text(text_element)
            if not text or len(text.strip()) < 10:
                return None
            
            # Extract rating
            rating = None
            rating_element = container.find('i', class_=re.compile(r'a-icon-star'))
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = self._safe_float_convert(rating_match.group(1))
            
            # Extract author
            author = None
            author_element = container.find('span', class_='a-profile-name')
            if author_element:
                author = self._extract_text(author_element)
            
            # Extract date
            date = None
            date_element = container.find('span', {'data-hook': 'review-date'})
            if date_element:
                date = self._extract_text(date_element)
            
            # Extract title
            title = None
            title_element = container.find('a', {'data-hook': 'review-title'})
            if title_element:
                title = self._extract_text(title_element)
            
            # Extract helpful votes
            helpful_votes = None
            helpful_element = container.find('span', {'data-hook': 'helpful-vote-statement'})
            if helpful_element:
                helpful_text = self._extract_text(helpful_element)
                helpful_match = re.search(r'(\d+)', helpful_text)
                if helpful_match:
                    helpful_votes = self._safe_int_convert(helpful_match.group(1))
            
            # Check if verified purchase
            verified = bool(container.find('span', {'data-hook': 'avp-badge'}))
            
            return ReviewData(
                text=text,
                rating=rating,
                author=author,
                date=date,
                title=title,
                helpful_votes=helpful_votes,
                verified=verified,
                source_url=source_url,
                platform='Amazon'
            )
            
        except Exception as e:
            logger.error(f"Error extracting review data: {e}")
            return None
    
    def search_products(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on Amazon.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of product information dictionaries
        """
        products = []
        
        try:
            # Construct search URL
            search_url = f"https://amazon.com/s?k={query.replace(' ', '+')}"
            
            response = self._make_request(search_url)
            if not response:
                return products
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:max_results]:
                try:
                    product = self._extract_product_info(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.error(f"Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return products
    
    def _extract_product_info(self, container) -> Dict:
        """
        Extract product information from search result container.
        
        Args:
            container: BeautifulSoup element
            
        Returns:
            Product information dictionary
        """
        try:
            # Extract title
            title_element = container.find('h2', class_='a-size-mini')
            if not title_element:
                title_element = container.find('span', class_='a-text-normal')
            
            title = self._extract_text(title_element) if title_element else "Unknown"
            
            # Extract URL
            url = None
            link_element = container.find('a', class_='a-link-normal')
            if link_element and link_element.get('href'):
                url = 'https://amazon.com' + link_element['href']
            
            # Extract rating
            rating = None
            rating_element = container.find('span', class_='a-icon-alt')
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = self._safe_float_convert(rating_match.group(1))
            
            # Extract price
            price = None
            price_element = container.find('span', class_='a-price-whole')
            if price_element:
                price_text = self._extract_text(price_element)
                price = self._safe_float_convert(price_text)
            
            return {
                'title': title,
                'url': url,
                'rating': rating,
                'price': price,
                'platform': 'Amazon'
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None 