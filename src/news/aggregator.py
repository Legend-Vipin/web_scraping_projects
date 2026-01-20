"""News headline aggregator with retry logic and common utilities."""

import asyncio
import httpx
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import common utilities
from src.common import (
    setup_logger,
    get_config,
    validate_news_data,
    filter_valid_data,
    sanitize_text,
)

# Configuration
config = get_config()

# Setup logger
logger = setup_logger(
    name="NewsAggregator",
    log_file="news_aggregator.log",
    level=10 if config.debug else 20  # DEBUG if debug mode, else INFO
)


class NewsAggregator:
    """Aggregates news headlines from multiple sources with retry logic."""
    
    def __init__(self):
        self.data:  List[Dict] = []
        self.timeout = httpx.Timeout(config.request_timeout)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
        }
    
    @retry(
        stop=stop_after_attempt(config.max_retries),
        wait=wait_exponential(multiplier=1, min=config.request_delay_min, max=config.request_delay_max),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True
    )
    async def _fetch_with_retry(self, client: httpx.AsyncClient, url: str) -> httpx.Response:
        """
        Fetch URL with automatic retry on failure.
        
        Args:
            client: HTTP client instance
            url: URL to fetch
        
        Returns:
            HTTP response
        """
        logger.debug(f"Fetching: {url}")
        response = await client.get(url, headers=self._get_headers(), timeout=self.timeout)
        response.raise_for_status()
        return response
    
    async def scrape_toi(self, client: httpx.AsyncClient):
        """Scrape Times of India headlines."""
        url = "https://timesofindia.indiatimes.com/home/headlines"
        
        try:
            response = await self._fetch_with_retry(client, url)
            
            from bs4 import BeautifulSoup
            soup =BeautifulSoup(response.content, 'lxml')
            
            # TOI headlines
            headlines = soup.select("span.w_tle > a") or soup.select(".main-content a")
            count = 0
            
            for h in headlines:
                text = sanitize_text(h.get_text())
                link = h.get('href', '')
                
                if text and link:
                    if not link.startswith('http'):
                        link = f"https://timesofindia.indiatimes.com{link}"
                    
                    self.data.append({
                        "source": "Times of India",
                        "headline": text,
                        "link": link,
                        "timestamp": datetime.now().isoformat()
                    })
                    count += 1
            
            logger.info(f"TOI: Collected {count} headlines")
            
        except Exception as e:
            logger.error(f"TOI scraping failed: {e}")
    
    async def scrape_hindu(self, client: httpx.AsyncClient):
        """Scrape The Hindu headlines."""
        url = "https://www.thehindu.com/"
        
        try:
            response = await self._fetch_with_retry(client, url)
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            
            # The Hindu headlines
            headlines = soup.select("h3.title a") or soup.select(".story-card-news h3 a")
            count = 0
            
            for h in headlines:
                text = sanitize_text(h.get_text())
                link = h.get('href', '')
                
                if text and link:
                    self.data.append({
                        "source": "The Hindu",
                        "headline": text,
                        "link": link,
                        "timestamp": datetime.now().isoformat()
                    })
                    count += 1
            
            logger.info(f"The Hindu: Collected {count} headlines")
            
        except Exception as e:
            logger.error(f"The Hindu scraping failed: {e}")
    
    async def scrape_ndtv(self, client: httpx.AsyncClient):
        """Scrape NDTV headlines."""
        url = "https://www.ndtv.com/top-stories"
        
        try:
            response = await self._fetch_with_retry(client, url)
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            
            # NDTV headlines
            headlines = soup.select(".news_Itm-cont h2 a")
            count = 0
            
            for h in headlines:
                text = sanitize_text(h.get_text())
                link = h.get('href', '')
                
                if text and link:
                    self.data.append({
                        "source": "NDTV",
                        "headline": text,
                        "link": link,
                        "timestamp": datetime.now().isoformat()
                    })
                    count += 1
            
            logger.info(f"NDTV: Collected {count} headlines")
            
        except Exception as e:
            logger.error(f"NDTV scraping failed: {e}")
    
    async def run(self):
        """Run all scrapers concurrently."""
        logger.info("Starting news aggregation...")
        
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(config.request_timeout),
            follow_redirects=True
        ) as client:
            await asyncio.gather(
                self.scrape_toi(client),
                self.scrape_hindu(client),
                self.scrape_ndtv(client),
                return_exceptions=True  # Don't fail all if one fails
            )
    
    def save_data(self):
        """Save collected data with validation."""
        if not self.data:
            logger.warning("No data collected")
            return
        
        # Validate and filter data
        valid_data = filter_valid_data(self.data, validate_news_data)
        invalid_count = len(self.data) - len(valid_data)
        
        if invalid_count > 0:
            logger.warning(f"Filtered out {invalid_count} invalid entries")
        
        if not valid_data:
            logger.warning("No valid data to save")
            return
        
        # Generate filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = config.data_dir / f"headlines_{timestamp}.csv"
        json_file = config.data_dir / f"headlines_{timestamp}.json"
        
        # Save based on output format setting
        import pandas as pd
        df = pd.DataFrame(valid_data)
        
        if config.output_format in ["csv", "both"]:
            df.to_csv(csv_file, index=False)
            logger.info(f"Saved {len(df)} headlines to {csv_file}")
        
        if config.output_format in ["json", "both"]:
            df.to_json(json_file, orient='records', indent=2)
            logger.info(f"Saved {len(df)} headlines to {json_file}")


def main():
    """Main entry point."""
    aggregator = NewsAggregator()
    
    try:
        asyncio.run(aggregator.run())
        aggregator.save_data()
        logger.info("News aggregation complete")
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Aggregation failed: {e}", exc_info=config.debug)


if __name__ == "__main__":
    main()
