from loguru import logger
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from firecrawl import Firecrawl

from core.config.settings import settings


class FirecrawlClient:
    """Client for interacting with Firecrawl API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.firecrawl_api_key
        self.client = Firecrawl(api_key=self.api_key) if self.api_key else None

        # URL patterns to exclude during crawling
        self.exclude_patterns = {
            'privacy', 'cookie', 'terms', 'legal', 'contact-form',
            'subscribe', 'newsletter', 'login', 'signup', 'cart',
            'checkout', 'account', 'admin', 'wp-admin', 'pdf',
            'download', 'mailto:', 'tel:', 'javascript:'
        }

        # URL patterns that are valuable for business intelligence
        self.valuable_patterns = {
            'about', 'team', 'leadership', 'services', 'solutions',
            'products', 'case-studies', 'portfolio', 'clients',
            'approach', 'methodology', 'culture', 'values',
            'history', 'story', 'mission', 'vision', 'blog',
            'news', 'insights', 'careers', 'jobs'
        }

    async def discover_urls(self, base_url: str) -> list[str]:
        """
        Discover all URLs within a website using Firecrawl's map functionality
        """
        if not self.client:
            logger.error("No Firecrawl API key provided - cannot discover URLs")
            raise ValueError("Firecrawl API key is required for URL discovery")

        try:
            # map() returns an object with a 'links' attribute
            result = self.client.map(url=base_url, limit=settings.max_urls_to_scrape)
            
            # Extract the links list from the result object
            links = result.links if hasattr(result, 'links') else result
            
            # Handle case where links might be None or empty
            if not links:
                logger.warning(f"No links discovered from {base_url}")
                return []

            # Extract URLs from LinkResult objects
            urls = [link.url for link in links if link.url and link.url.strip()]

            logger.info(f"Discovered {len(urls)} URLs from {base_url}")
            return urls

        except Exception as e:
            logger.error(f"Error discovering URLs from {base_url}: {e}")
            raise
    def filter_valuable_urls(self, urls: list[str]) -> list[str]:
        """
        Intelligently filter URLs to find those most valuable for business intelligence
        """
        scored_urls = []
        
        for url in urls:
            score = self._score_url_value(url)
            if score > 0:
                scored_urls.append((url, score))
        
        # Sort by score (descending) and take top URLs
        scored_urls.sort(key=lambda x: x[1], reverse=True)
        filtered_urls = [url for url, _ in scored_urls[:settings.max_urls_to_scrape]]
        
        logger.info(f"Filtered {len(urls)} URLs down to {len(filtered_urls)} valuable URLs")
        return filtered_urls

    def _score_url_value(self, url: str) -> float:
        """
        Score a URL based on its potential value for business intelligence
        Returns 0 for excluded URLs, higher scores for more valuable URLs
        """
        from urllib.parse import urlparse
        
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        # Exclude unwanted URLs
        for pattern in self.exclude_patterns:
            if pattern in url_lower:
                return 0.0
        
        # Score valuable URLs
        score = 1.0  # Base score for any non-excluded URL
        
        for pattern in self.valuable_patterns:
            if pattern in url_lower:
                score += 2.0
                
        # Bonus for common business pages
        if any(term in path for term in ['/about', '/team', '/services']):
            score += 3.0
            
        # Penalty for very long URLs (likely not main pages)
        if len(url) > 100:
            score -= 1.0
            
        # Bonus for shorter paths (likely more important pages)
        path_depth = len([p for p in path.split('/') if p])
        if path_depth <= 2:
            score += 1.0
            
        return max(0.0, score)
    
    async def scrape_multiple_urls(self, urls: list[str]) -> dict[str, str]:
        """
        Scrape content from multiple URLs with rate limiting
        """
        scraped_content = {}
        
        for i, url in enumerate(urls):
            try:
                # Add small delay between requests to respect rate limits
                if i > 0:
                    import time
                    time.sleep(1)  # 1 second delay between requests
                
                result = await self.scrape_url(url)
                scraped_content[url] = result['content']
                logger.info(f"Successfully scraped {i+1}/{len(urls)}: {url}")
                
            except Exception as e:
                error_msg = f"Failed to scrape {url}: {str(e)}"
                logger.warning(error_msg)
                scraped_content[url] = f"Error: {str(e)}"
        
        return scraped_content
    
    async def scrape_url(self, url: str) -> dict[str, str]:
        """
        Scrape content from a single URL using Firecrawl
        """
        if not self.client:
            logger.error("No Firecrawl API key provided - cannot scrape content")
            raise ValueError("Firecrawl API key is required for content scraping")
        
        try:
            # Use markdown format for better LLM processing
            result = self.client.scrape(url=url, formats=['markdown'])
            
            if result and result.markdown:
                content = result.markdown
                # Truncate if too long
                if len(content) > settings.max_content_length:
                    content = content[:settings.max_content_length] + "...[truncated]"
                
                return {
                    'url': url,
                    'content': content,
                    'format': 'markdown'
                }
            else:
                logger.error(f"Failed to scrape {url}: No content returned")
                raise Exception(f"Firecrawl scraping failed: No content returned")
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            raise

        