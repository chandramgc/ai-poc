"""
Unit tests for the Google search scraper.

Tests cover:
- Successful search result parsing
- Error handling (rate limiting, network errors)
- Cache behavior
- Retry logic with exponential backoff
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import RequestException, Timeout

from app.scraper.google_search import (
    GoogleSearchScraper,
    ScraperError,
    RateLimitError
)
from app.models.article import Article


# Sample HTML response for testing
SAMPLE_GOOGLE_HTML = """
<html>
<body>
<div class="g">
    <a href="https://example.com/insulin-news-1">
        <h3>New Insulin Treatment Shows Promise</h3>
    </a>
    <div class="VwiC3b">Researchers have developed a new insulin formulation that could help millions...</div>
    <cite>Medical News Today</cite>
    <span class="f">2 days ago</span>
</div>
<div class="g">
    <a href="https://example.com/insulin-study-2">
        <h3>Insulin Study Reveals Key Findings</h3>
    </a>
    <div class="VwiC3b">A comprehensive study on insulin resistance has revealed important insights...</div>
    <cite>Health Journal</cite>
    <span class="f">1 week ago</span>
</div>
<div class="g">
    <a href="https://example.com/diabetes-breakthrough">
        <h3>Breakthrough in Diabetes Treatment</h3>
    </a>
    <div class="VwiC3b">Scientists announce breakthrough in managing type 2 diabetes...</div>
    <cite>Science Daily</cite>
</div>
</body>
</html>
"""

BLOCKED_HTML = """
<html>
<body>
<h1>We detected unusual traffic from your computer network</h1>
<p>Please complete the CAPTCHA to continue.</p>
</body>
</html>
"""


class TestGoogleSearchScraper:
    """Test suite for GoogleSearchScraper."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return GoogleSearchScraper()
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock HTTP response."""
        response = Mock()
        response.status_code = 200
        response.text = SAMPLE_GOOGLE_HTML
        response.raise_for_status = Mock()
        return response
    
    def test_scraper_initialization(self, scraper):
        """Test that scraper initializes correctly."""
        assert scraper is not None
        assert scraper.session is not None
        assert "User-Agent" in scraper.session.headers
    
    def test_build_search_url(self, scraper):
        """Test URL construction for search queries."""
        url = scraper._build_search_url("Insulin")
        assert "google.com/search" in url
        assert "q=Insulin" in url
        assert "tbm=nws" in url  # News search
    
    @patch("app.scraper.google_search.requests.Session.get")
    @patch("app.scraper.google_search.time.sleep")
    def test_successful_search(self, mock_sleep, mock_get, scraper, mock_response):
        """Test successful search and parsing."""
        mock_get.return_value = mock_response
        
        results = scraper.search("Insulin", limit=3)
        
        assert len(results) <= 3
        assert all(isinstance(article, Article) for article in results)
        
        # Check first result
        if results:
            first = results[0]
            assert first.title
            assert str(first.url).startswith("http")
            assert first.snippet
    
    @patch("app.scraper.google_search.requests.Session.get")
    def test_rate_limit_detection(self, mock_get, scraper):
        """Test detection of rate limiting (HTTP 429)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            scraper.search("Insulin")
    
    @patch("app.scraper.google_search.requests.Session.get")
    def test_blocked_detection(self, mock_get, scraper):
        """Test detection of Google anti-bot challenge."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = BLOCKED_HTML
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with pytest.raises(RateLimitError, match="anti-bot"):
            scraper.search("Insulin")
    
    @patch("app.scraper.google_search.requests.Session.get")
    @patch("app.scraper.google_search.time.sleep")
    def test_retry_logic(self, mock_sleep, mock_get, scraper, mock_response):
        """Test exponential backoff retry logic."""
        # First two calls fail, third succeeds
        mock_get.side_effect = [
            Timeout("Connection timeout"),
            Timeout("Connection timeout"),
            mock_response
        ]
        
        results = scraper.search("Insulin")
        
        # Should have retried and eventually succeeded
        assert mock_get.call_count == 3
        assert mock_sleep.call_count >= 2  # Called for retries
        assert len(results) >= 0
    
    @patch("app.scraper.google_search.requests.Session.get")
    @patch("app.scraper.google_search.time.sleep")
    def test_retry_exhaustion(self, mock_sleep, mock_get, scraper):
        """Test that scraper raises error after max retries."""
        mock_get.side_effect = Timeout("Connection timeout")
        
        with pytest.raises(ScraperError, match="Failed to fetch"):
            scraper.search("Insulin")
        
        # Should have attempted max_retries times
        from app.core.config import settings
        assert mock_get.call_count == settings.max_retries
    
    def test_is_blocked_detection(self, scraper):
        """Test blocked page detection logic."""
        assert scraper._is_blocked(BLOCKED_HTML) is True
        assert scraper._is_blocked(SAMPLE_GOOGLE_HTML) is False
    
    def test_parse_search_results(self, scraper):
        """Test parsing of HTML search results."""
        articles = scraper._parse_search_results(SAMPLE_GOOGLE_HTML, limit=10)
        
        assert len(articles) >= 2
        
        # Verify first article
        first = articles[0]
        assert "Insulin" in first.title or "Treatment" in first.title
        assert str(first.url).startswith("https://example.com")
        assert first.snippet
    
    def test_parse_empty_results(self, scraper):
        """Test parsing when no results are found."""
        empty_html = "<html><body></body></html>"
        articles = scraper._parse_search_results(empty_html, limit=10)
        
        assert articles == []
    
    def test_extract_article_data(self, scraper):
        """Test extraction of article data from HTML element."""
        from bs4 import BeautifulSoup
        
        html = """
        <div class="g">
            <a href="https://example.com/article">
                <h3>Test Article Title</h3>
            </a>
            <div class="VwiC3b">This is a test snippet</div>
            <cite>Test Source</cite>
            <span class="f">1 day ago</span>
        </div>
        """
        
        soup = BeautifulSoup(html, "lxml")
        element = soup.select_one("div.g")
        
        article = scraper._extract_article_data(element)
        
        assert article is not None
        assert article.title == "Test Article Title"
        assert str(article.url) == "https://example.com/article"
        assert article.snippet == "This is a test snippet"
    
    def test_limit_parameter(self, scraper):
        """Test that limit parameter is respected."""
        articles = scraper._parse_search_results(SAMPLE_GOOGLE_HTML, limit=2)
        
        assert len(articles) <= 2


class TestScraperFactory:
    """Test scraper factory function."""
    
    def test_get_scraper_bs4(self):
        """Test getting bs4 scraper."""
        from app.scraper.google_search import get_scraper
        from app.core.config import settings
        
        # Ensure bs4 backend is set
        original_backend = settings.scraper_backend
        settings.scraper_backend = "bs4"
        
        try:
            scraper = get_scraper()
            assert isinstance(scraper, GoogleSearchScraper)
        finally:
            settings.scraper_backend = original_backend
    
    def test_get_scraper_unsupported_backend(self):
        """Test error for unsupported backend."""
        from app.scraper.google_search import get_scraper
        from app.core.config import settings
        
        original_backend = settings.scraper_backend
        settings.scraper_backend = "playwright"
        
        try:
            with pytest.raises(NotImplementedError, match="playwright"):
                get_scraper()
        finally:
            settings.scraper_backend = original_backend


class TestCacheIntegration:
    """Test cache integration with scraper."""
    
    @pytest.fixture
    def mock_cache(self):
        """Create a mock cache."""
        with patch("app.api.routes.cache") as mock:
            mock.get.return_value = None
            mock.set.return_value = None
            yield mock
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, mock_cache):
        """Test cache miss triggers scraper."""
        from app.api.routes import search_articles
        
        with patch("app.api.routes.get_scraper") as mock_scraper:
            mock_instance = Mock()
            mock_instance.search.return_value = [
                Article(
                    title="Test",
                    url="https://example.com",
                    snippet="Test snippet",
                    source="Test Source"
                )
            ]
            mock_scraper.return_value = mock_instance
            
            response = await search_articles(q="Insulin", limit=10)
            
            assert mock_cache.get.called
            assert mock_cache.set.called
            assert response.cached is False
            assert len(response.results) == 1
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_cache):
        """Test cache hit returns cached results."""
        from app.api.routes import search_articles
        
        cached_articles = [
            Article(
                title="Cached Article",
                url="https://example.com/cached",
                snippet="Cached snippet",
                source="Cache"
            )
        ]
        mock_cache.get.return_value = cached_articles
        
        response = await search_articles(q="Insulin", limit=10)
        
        assert response.cached is True
        assert len(response.results) == 1
        assert response.results[0].title == "Cached Article"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
