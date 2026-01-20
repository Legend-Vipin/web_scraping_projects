import asyncio
import argparse
import random
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
from fake_useragent import UserAgent

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crawler.log')
    ]
)
logger = logging.getLogger(__name__)

class RealEstateCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.data: List[Dict] = []
        self.ua = UserAgent()

    def _get_random_user_agent(self):
        try:
            return self.ua.random
        except:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def _get_page_content(self, page: Page, url: str) -> Optional[str]:
        try:
            logger.info(f"Navigating to {url}...")
            await page.set_extra_http_headers({
                "User-Agent": self._get_random_user_agent()
            })
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(3000, 5000))
            return await page.content()
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def scrape_99acres(self, city: str):
        # 99acres URL
        url = f"https://www.99acres.com/search/property/buy/{city.lower()}?keyword={city}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            content = await self._get_page_content(page, url)
            if not content:
                await browser.close()
                return

            soup = BeautifulSoup(content, 'lxml')
            
            # 99acres tuples
            # Common classes: projectTuple, srpTuple
            items = soup.find_all('div', {'class': 'projectTuple'}) or soup.find_all('div', {'class': 'srpTuple__tupleTable'})
            if not items:
                # Try generic search for price blocks
                items = soup.find_all('div', class_=lambda x: x and 'tuple' in x.lower())

            logger.info(f"Found {len(items)} properties.")
            
            for item in items:
                try:
                    title_el = item.find('a', {'class': 'srpTuple__propertyName'}) or item.find('a', {'class': 'projectTuple__projectName'})
                    price_el = item.find('td', {'class': 'srpTuple__price'}) or item.find('div', {'class': 'list_header_semiBold'})
                    loc_el = item.find('a', {'class': 'srpTuple__localityName'}) or item.find('div', {'class': 'projectTuple__subHeadingWithLocality'})

                    if not title_el:
                        continue
                    
                    self.data.append({
                        "title": title_el.text.strip(),
                        "price": price_el.text.strip() if price_el else "Price on Request",
                        "location": loc_el.text.strip() if loc_el else city,
                        "link": title_el.get('href', ''),
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    continue

            await browser.close()

    def save_data(self):
        if not self.data:
            logger.warning("No data collected.")
            return

        df = pd.DataFrame(self.data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"realestate_{timestamp}.csv"
        
        df.to_csv(csv_file, index=False)
        logger.info(f"Saved {len(df)} properties to {csv_file}")
        print("\n--- PROPERTIES FOUND ---")
        print(df.head().to_string())

def main():
    parser = argparse.ArgumentParser(description="Real Estate Crawler")
    parser.add_argument("--city", type=str, default="pune", help="City to search")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()

    crawler = RealEstateCrawler(headless=args.headless)
    asyncio.run(crawler.scrape_99acres(args.city))
    crawler.save_data()

if __name__ == "__main__":
    main()
