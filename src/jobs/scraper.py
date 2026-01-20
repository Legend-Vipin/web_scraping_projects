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
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.data: List[Dict] = []
        self.ua = UserAgent()

    def _get_random_user_agent(self):
        try:
            return self.ua.random
        except Exception:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def _get_page_content(self, page: Page, url: str, wait_selector: str = 'body') -> Optional[str]:
        try:
            logger.info(f"Navigating to {url}...")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(3000, 6000))
            
            try:
                await page.wait_for_selector(wait_selector, timeout=15000)
            except Exception:
                logger.warning(f"Selector {wait_selector} not found.")

            return await page.content()
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    async def scrape_naukri(self, role: str, location: str):
        """Scrapes Naukri.com."""
        # Naukri URL structure
        role_enc = role.replace(" ", "-").lower()
        loc_enc = location.replace(" ", "-").lower()
        url = f"https://www.naukri.com/{role_enc}-jobs-in-{loc_enc}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Naukri uses 'srp-tuple-layout' or similar classes
            # Try multiple selectors
            content = await self._get_page_content(page, url, "div.srp-jobtuple-wrapper, article.jobTuple, div.list")
            if not content:
                await browser.close()
                return

            soup = BeautifulSoup(content, 'lxml')
            
            # Select job tuples with fallbacks
            jobs = soup.find_all('div', {'class': 'srp-jobtuple-wrapper'})
            if not jobs:
                jobs = soup.find_all('article', {'class': 'jobTuple'})
            if not jobs:
                jobs = soup.find_all('div', {'class': 'list'}) 
                
            logger.info(f"Found {len(jobs)} jobs.")
            
            for job in jobs:
                try:
                    title_el = job.find('a', {'class': 'title'})
                    company_el = job.find('a', {'class': 'comp-name'}) or job.find('a', {'class': 'subTitle'})
                    
                    # Experience, Salary, Location are usually in a list
                    exp_el = job.find('span', {'class': 'exp-wrap'}) or job.find('span', {'class': 'exp'}) or job.find('li', {'class': 'experience'})
                    sal_el = job.find('span', {'class': 'sal-wrap'}) or job.find('span', {'class': 'sal'}) or job.find('li', {'class': 'salary'})
                    loc_el = job.find('span', {'class': 'loc-wrap'}) or job.find('span', {'class': 'loc'}) or job.find('li', {'class': 'location'})
                    
                    if not title_el:
                        continue

                    title = title_el.text.strip()
                    company = company_el.text.strip() if company_el else "Confidential"
                    experience = exp_el.text.strip() if exp_el else "Not specified"
                    salary = sal_el.text.strip() if sal_el else "Not disclosed"
                    location = loc_el.text.strip() if loc_el else "Not specified"
                    
                    link = title_el['href'] if title_el else ""

                    self.data.append({
                        "title": title,
                        "company": company,
                        "experience": experience,
                        "salary": salary,
                        "location": location,
                        "link": link,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Error parsing job: {e}")

            await browser.close()

    def save_data(self):
        if not self.data:
            logger.warning("No data collected.")
            return

        df = pd.DataFrame(self.data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"jobs_{timestamp}.csv"
        json_file = f"jobs_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient='records', indent=2)
        logger.info(f"Saved {len(df)} jobs to {csv_file}")
        
        print("\n--- TOP JOBS FOUND ---")
        print(df[['title', 'company', 'salary']].head().to_string())

def main():
    parser = argparse.ArgumentParser(description="Job Portal Scraper (Naukri)")
    parser.add_argument("--role", type=str, default="python developer", help="Job role")
    parser.add_argument("--location", type=str, default="remote", help="Job location")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.set_defaults(headless=True)
    
    args = parser.parse_args()

    scraper = JobScraper(headless=args.headless)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(scraper.scrape_naukri(args.role, args.location))
    except Exception as e:
        logger.error(f"Scrape failed: {e}")
    
    scraper.save_data()

if __name__ == "__main__":
    main()
