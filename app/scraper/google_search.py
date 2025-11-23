"""
Google search scraper using BeautifulSoup (bs4 backend).

This module implements a polite web scraper for Google search results,
with rate limiting, retry logic, and proper error handling.
"""
import logging
import time
from typing import List, Optional
from urllib.parse import quote_plus, urlencode

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.article import Article

logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limited or blocked by Google."""
    pass


class GoogleSearchScraper:
    """
    Google search scraper using requests + BeautifulSoup.
    
    Implements:
    - Polite HTTP requests with configurable delays
    - Exponential backoff retry logic
    - robots.txt respect (note in logs)
    - Google anti-bot detection
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        logger.info(
            "GoogleSearchScraper initialized. "
            "Note: Please respect robots.txt and Google's Terms of Service."
        )
    
    def search(self, query: str, limit: int = 10) -> List[Article]:
        """
        Search Google for the given query and parse results.
        
        Args:
            query: Search query (e.g., "Insulin news")
            limit: Maximum number of results to return (default 10)
            
        Returns:
            List of Article objects
            
        Raises:
            ScraperError: On scraping failures
            RateLimitError: When blocked by Google
        """
        logger.info(f"Searching Google for: {query} (limit: {limit})")
        
        # Test mode - return mock data for development/testing
        if settings.test_mode:
            logger.info("TEST_MODE enabled - returning mock data")
            return self._get_mock_data(query, limit)
        
        # Construct Google search URL
        search_url = self._build_search_url(query)
        
        # Fetch with retry logic
        html = self._fetch_with_retry(search_url)
        
        # Parse results
        articles = self._parse_search_results(html, limit)
        
        logger.info(f"Successfully scraped {len(articles)} results")
        return articles
    
    def _build_search_url(self, query: str) -> str:
        """Build Google search URL for the query."""
        # Using Google News search for medicine-related queries
        params = {
            "q": query,
            "tbm": "nws",  # News search
            "num": min(settings.max_results, 20)  # Request more than needed
        }
        return f"https://www.google.com/search?{urlencode(params)}"
    
    def _fetch_with_retry(self, url: str) -> str:
        """
        Fetch URL with exponential backoff retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content
            
        Raises:
            ScraperError: On persistent failures
            RateLimitError: When blocked by Google
        """
        last_exception = None
        
        for attempt in range(settings.max_retries):
            try:
                # Add delay between requests (rate limiting)
                if attempt > 0:
                    backoff = settings.request_delay * (settings.retry_backoff_factor ** attempt)
                    logger.info(f"Retry attempt {attempt + 1}, waiting {backoff:.2f}s")
                    time.sleep(backoff)
                # No initial delay on first attempt for better responsiveness
                
                logger.debug(f"Fetching URL: {url}")
                logger.debug(f"Timeout: {settings.request_timeout}s")
                
                response = self.session.get(
                    url,
                    timeout=settings.request_timeout,
                    allow_redirects=True
                )
                
                # Check for rate limiting / blocking
                if response.status_code == 429:
                    raise RateLimitError("Rate limited by Google (HTTP 429)")
                
                if response.status_code == 503:
                    raise RateLimitError("Service unavailable (HTTP 503) - possibly blocked")
                
                response.raise_for_status()
                
                logger.debug(f"Response status: {response.status_code}, size: {len(response.text)} bytes")
                
                # Check for CAPTCHA or block page
                if self._is_blocked(response.text):
                    logger.warning("Google anti-bot challenge detected")
                    raise RateLimitError(
                        "Detected Google anti-bot challenge. "
                        "Consider using Playwright backend or reducing request rate."
                    )
                
                logger.info("Successfully fetched search results")
                return response.text
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                last_exception = e
        
        # All retries exhausted
        raise ScraperError(
            f"Failed to fetch search results after {settings.max_retries} attempts: {last_exception}"
        )
    
    def _is_blocked(self, html: str) -> bool:
        """
        Detect if Google is blocking/challenging the request.
        
        Args:
            html: Response HTML
            
        Returns:
            True if likely blocked/challenged
        """
        blocked_indicators = [
            "detected unusual traffic",
            "captcha",
            "sorry for the inconvenience",
            "/sorry/index"
        ]
        html_lower = html.lower()
        return any(indicator in html_lower for indicator in blocked_indicators)
    
    def _parse_search_results(self, html: str, limit: int) -> List[Article]:
        """
        Parse Google search results HTML.
        
        Args:
            html: HTML content from Google search
            limit: Maximum number of results to extract
            
        Returns:
            List of Article objects
        """
        soup = BeautifulSoup(html, "lxml")
        articles = []
        
        # Google News search results are typically in divs with specific classes
        # Note: Google's HTML structure changes frequently; this is a best-effort approach
        
        # Try multiple selectors (Google structure varies)
        result_selectors = [
            "div.SoaBEf",  # News results
            "div.Gx5Zad",  # Standard results
            "div.g",       # Generic result container
        ]
        
        results = []
        for selector in result_selectors:
            results = soup.select(selector)
            if results:
                logger.debug(f"Found results using selector: {selector}")
                break
        
        if not results:
            logger.warning("No results found - HTML structure may have changed")
            logger.debug(f"HTML preview: {html[:500]}")
        
        for result in results[:limit]:
            try:
                article = self._extract_article_data(result)
                if article:
                    articles.append(article)
            except Exception as e:
                logger.debug(f"Failed to parse result: {e}")
                continue
        
        return articles
    
    def _extract_article_data(self, result_element) -> Optional[Article]:
        """
        Extract article data from a search result element.
        
        Args:
            result_element: BeautifulSoup element containing result
            
        Returns:
            Article object or None if extraction fails
        """
        try:
            # Extract link
            link_elem = result_element.select_one("a")
            if not link_elem or not link_elem.get("href"):
                return None
            
            url = link_elem["href"]
            
            # Skip non-http links
            if not url.startswith("http"):
                return None
            
            # Extract title
            title_elem = result_element.select_one("h3, div[role='heading']")
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Extract snippet
            snippet_elem = result_element.select_one(
                "div.GI74Re, div.VwiC3b, div.s"
            )
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract source
            source_elem = result_element.select_one(
                "div.CEMjEf span, div.NUnG9d span, cite"
            )
            source = source_elem.get_text(strip=True) if source_elem else None
            
            # Extract published date (if available)
            date_elem = result_element.select_one(
                "div.OSrXXb span, span.f"
            )
            published_date = date_elem.get_text(strip=True) if date_elem else None
            
            return Article(
                title=title,
                url=url,
                snippet=snippet,
                source=source,
                published_date=published_date
            )
            
        except Exception as e:
            logger.debug(f"Failed to extract article data: {e}")
            return None
    
    def _get_mock_data(self, query: str, limit: int) -> List[Article]:
        """
        Return mock data for testing/development.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of mock Article objects
        """
        mock_articles = [
            Article(
                title=f"New {query} Treatment Shows Promise in Clinical Trials",
                url="https://example.com/news/treatment-breakthrough",
                snippet=f"Researchers have developed a new {query} formulation that could help millions of patients worldwide...",
                source="Medical News Today",
                published_date="2 days ago"
            ),
            Article(
                title=f"{query} Study Reveals Key Findings About Effectiveness",
                url="https://example.com/news/study-findings",
                snippet=f"A comprehensive study on {query} has revealed important insights into treatment efficacy...",
                source="Health Journal",
                published_date="1 week ago"
            ),
            Article(
                title=f"FDA Approves New {query}-Based Medication",
                url="https://example.com/news/fda-approval",
                snippet=f"The FDA has approved a new medication based on {query} research, marking a significant milestone...",
                source="Science Daily",
                published_date="3 days ago"
            ),
            Article(
                title=f"Breakthrough in {query} Research Could Change Treatment",
                url="https://example.com/news/research-breakthrough",
                snippet=f"Scientists announce breakthrough in {query} research that could revolutionize patient care...",
                source="Medical Research News",
                published_date="5 days ago"
            ),
            Article(
                title=f"Global {query} Market Expected to Grow Significantly",
                url="https://example.com/news/market-growth",
                snippet=f"Market analysis shows the global {query} market is projected to grow by 15% annually...",
                source="Healthcare Business",
                published_date="1 day ago"
            ),
        ]
        
        return mock_articles[:limit]


# Factory function for getting scraper instance
def get_scraper() -> GoogleSearchScraper:
    """Get scraper instance based on configured backend."""
    if settings.scraper_backend != "bs4":
        raise NotImplementedError(
            f"Backend '{settings.scraper_backend}' not implemented in this module. "
            f"Use 'bs4' backend or implement {settings.scraper_backend} scraper."
        )
    return GoogleSearchScraper()
