"""
Web scraping modules for feelnet.

This module contains scrapers for various platforms including
Amazon, IMDb, TripAdvisor and other review sites.
"""

from .scraper_factory import ScraperFactory
from .amazon_scraper import AmazonScraper
from .imdb_scraper import IMDbScraper
from .tripadvisor_scraper import TripAdvisorScraper
from .base_scraper import BaseScraper

__all__ = [
    "ScraperFactory",
    "AmazonScraper", 
    "IMDbScraper",
    "TripAdvisorScraper",
    "BaseScraper"
] 