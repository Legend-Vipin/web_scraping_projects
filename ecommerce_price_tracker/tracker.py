import asyncio
import argparse
import random
import sys
import logging
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError
from fake_useragent import UserAgent

# --- 1. Logging Setup ---
class CustomFormatter(logging.Formatter):
    """Custom logging format with timestamps."""
    format = "%(asctime)s - %(levelname)s - %(message)s"
    
    def format(self, record):
        record.asctime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super().format(record)

def setup_logger():
    logger = logging.getLogger("EcommerceTracker")
    logger.setLevel(logging.INFO)
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    
    # File Handler
    fh = logging.FileHandler("tracker.log", mode='a', encoding='utf-8')
    fh.setFormatter(CustomFormatter())
    logger.addHandler(fh)
    
    return logger

logger = setup_logger()

# --- 2. Data Structure ---
class Product:
    def __init__(self, platform, title, price, rating, reviews, url, image_url, availability):
        self.platform = platform
        self.title = title
        self.price = price
        self.rating = rating
        self.reviews = reviews
        self.url = url
        self.image_url = image_url
        self.availability = availability

    def to_dict(self):
        return self.__dict__

# --- 3. Scraper Class ---
class EcommerceScraper:
    def __init__(self, query: str, max_pages: int = 5, headless: bool = True):
        self.query = query
        self.max_pages = max_pages
        self.headless = headless
        self.ua = UserAgent()
        self.results: List[Dict] = []
        self.seen_urls = set()
        
        # Verify Directory
        self.base_dir = Path(__file__).parent
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)
            logger.info(f"Created directory: {self.base_dir}")
        else:
            logger.info(f"Directory verified: {self.base_dir}")

    async def _get_stealth_context(self, browser):
        # Randomize Viewport
        width = random.randint(1366, 1920)
        height = random.randint(768, 1080)
        
        context = await browser.new_context(
            user_agent=self.ua.random,
            viewport={'width': width, 'height': height},
            locale='en-IN',
            timezone_id='Asia/Kolkata',
            java_script_enabled=True,
            accept_downloads=False
        )
        
        # Anti-detection scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        return context

    async def _safe_goto(self, page: Page, url: str) -> bool:
        try:
            logger.info(f"Navigating to: {url}")
            await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort()) # Block images
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(2.0, 5.0)) # Initial random delay
            return True
        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            return False

    async def _auto_scroll(self, page: Page):
        """Gradually scroll to trigger lazy loading."""
        try:
            logger.info("Auto-scrolling page...")
            prev_height = -1
            max_scrolls = 5
            for _ in range(max_scrolls):
                await page.evaluate("window.scrollBy(0, 600)")
                await asyncio.sleep(random.uniform(0.5, 1.5))
                curr_height = await page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    break
                prev_height = curr_height
        except Exception as e:
            logger.warning(f"Scroll warning: {e}")

    def _clean_price(self, price_raw: str) -> Optional[int]:
        if not price_raw: return None
        try:
            clean = ''.join(filter(lambda x: x.isdigit(), price_raw))
            return int(clean) if clean else None
        except:
            return None

    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        for sel in selectors:
            try:
                found = element.select_one(sel)
                if found:
                    return found.get_text(strip=True)
            except:
                continue
        return None

    def _extract_attr(self, element, selectors: List[str], attr: str) -> Optional[str]:
        for sel in selectors:
            try:
                found = element.select_one(sel)
                if found and found.has_attr(attr):
                    return found[attr]
            except:
                continue
        return None

    # --- AMAZON SCRAPER ---
    async def scrape_amazon(self):
        logger.info(f"--- Starting Amazon Scrape: '{self.query}' ---")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await self._get_stealth_context(browser)
            page = await context.new_page()

            base_url = "https://www.amazon.in"
            search_url = f"{base_url}/s?k={self.query.replace(' ', '+')}"
            
            current_url = search_url
            
            for page_num in range(1, self.max_pages + 1):
                logger.info(f"Processing Amazon Page {page_num}...")
                
                if not await self._safe_goto(page, current_url):
                    break
                
                await self._auto_scroll(page)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Check for blocking/captcha
                if "Enter the characters you see below" in soup.text:
                    logger.error("Amazon CAPTCHA detected! Aborting Amazon scrape.")
                    break

                # Container Selectors
                containers = soup.select("div[data-component-type='s-search-result']")
                if not containers:
                    logger.warning(f"No items found on page {page_num}.")
                    break

                new_items = 0
                for item in containers:
                    try:
                        title = self._extract_text(item, ["h2 a span", "h2", "span.a-text-normal"])
                        if not title: continue

                        # Unique ID Check
                        link_suffix = self._extract_attr(item, ["h2 a", "a.a-link-normal"], "href")
                        if not link_suffix: continue
                        url = urljoin(base_url, link_suffix)
                        
                        unique_key = f"Amazon_{url}"
                        if unique_key in self.seen_urls: continue
                        self.seen_urls.add(unique_key)
                        
                        # Extract other fields
                        price_raw = self._extract_text(item, ["span.a-price-whole", "span.a-offscreen"])
                        price = self._clean_price(price_raw)
                        
                        rating = self._extract_text(item, ["span.a-icon-alt", "i.a-icon-star-small"])
                        if rating: rating = rating.split(' ')[0]
                        
                        reviews = self._extract_text(item, ["span.a-size-base.s-underline-text", "span.a-size-base"])
                        
                        img_url = self._extract_attr(item, ["img.s-image"], "src")
                        
                        # Determine Availability
                        availability = "In Stock" if price else "Out of Stock"
                        if "Currently unavailable" in (self._extract_text(item, ["span.a-color-price"]) or ""):
                            availability = "Out of Stock"

                        product = Product(
                            platform="Amazon",
                            title=title,
                            price=price,
                            rating=rating,
                            reviews=reviews,
                            url=url,
                            image_url=img_url,
                            availability=availability
                        )
                        self.results.append(product.to_dict())
                        new_items += 1
                        
                    except Exception as e:
                        logger.warning(f"Error parsing item: {e}")
                        continue
                
                logger.info(f"Page {page_num}: Extracted {new_items} items.")
                
                # Pagination: Find 'Next' button
                next_btn = soup.select_one("a.s-pagination-next")
                if next_btn and "href" in next_btn.attrs:
                    current_url = urljoin(base_url, next_btn["href"])
                    await asyncio.sleep(random.uniform(2, 4))
                else:
                    logger.info("No next page found on Amazon.")
                    break
            
            await browser.close()

    # --- FLIPKART SCRAPER ---
    async def scrape_flipkart(self):
        logger.info(f"--- Starting Flipkart Scrape: '{self.query}' ---")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await self._get_stealth_context(browser)
            page = await context.new_page()

            base_url = "https://www.flipkart.com"
            search_url = f"{base_url}/search?q={self.query.replace(' ', '%20')}&sort=recency_desc"
            
            current_url = search_url
            
            for page_num in range(1, self.max_pages + 1):
                logger.info(f"Processing Flipkart Page {page_num}...")
                
                if not await self._safe_goto(page, current_url):
                    break
                
                await self._auto_scroll(page)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')

                # Flipkarts containers vary: grid vs list
                containers = soup.select("div._1AtVbE") + soup.select("div._75nlfW") # Fallback for different layouts
                
                # Filter useful containers (some are just spacers)
                valid_containers = []
                for c in containers:
                    if c.select_one("div[data-id]"):
                        valid_containers.append(c)
                
                # Try generic data-id selector if others fail
                if not valid_containers:
                    valid_containers = soup.select("div[data-id]")

                if not valid_containers:
                    logger.warning(f"No items found on page {page_num}.")
                    # Debug: save html
                    # with open(f"debug_flip_{page_num}.html", "w") as f: f.write(content)
                    break

                new_items = 0
                for item in valid_containers:
                    try:
                        # Skip if it doesn't look like a product
                        if not item.select_one("a[href]"): continue

                        # Title fallbacks
                        title = self._extract_text(item, ["div.KzDlHZ", "div._4rR01T", "a.s1Q9rs", "div.name"])
                        if not title:
                            # Search deeper for any text in link
                            link = item.select_one("a[href]")
                            if link: title = link.get_text(strip=True)
                        
                        if not title: continue

                        # URL
                        link_suffix = self._extract_attr(item, ["a.CGtC98", "a._1fQZEK", "a.s1Q9rs", "a[href]"], "href")
                        if not link_suffix: continue
                        url = urljoin(base_url, link_suffix)

                        unique_key = f"Flipkart_{url}"
                        if unique_key in self.seen_urls: continue
                        self.seen_urls.add(unique_key)

                        # Price
                        price_raw = self._extract_text(item, ["div.Nx9bqj", "div._30jeq3", "div._25b18c ._30jeq3"])
                        price = self._clean_price(price_raw)

                        # Rating
                        rating = self._extract_text(item, ["div.XQDdHH", "div._3LWZlK"]) # 4.5

                        # Reviews
                        reviews = self._extract_text(item, ["span.Wphh3N", "span._2_R_DZ"])
                        
                        # Image
                        img_url = self._extract_attr(item, ["img._396cs4", "img"], "src")

                        availability = "In Stock" if price else "Out of Stock"
                        if "Sold Out" in (self._extract_text(item, ["div._3Owiq+"]) or ""):
                            availability = "Out of Stock"

                        product = Product(
                            platform="Flipkart",
                            title=title,
                            price=price,
                            rating=rating,
                            reviews=reviews,
                            url=url,
                            image_url=img_url,
                            availability=availability
                        )
                        self.results.append(product.to_dict())
                        new_items += 1
                        
                    except Exception as e:
                        continue

                logger.info(f"Page {page_num}: Extracted {new_items} items.")

                # Pagination
                # Flipkart 'Next' button usually has 'Next' text or class '_1LKTO3'
                next_btn = soup.find('a', string="Next")
                if not next_btn:
                    next_btns = soup.select("a._1LKTO3")
                    if next_btns:
                        # Usually there are two (Prev, Next) or one. Check text or position
                        for btn in next_btns:
                            if "Next" in btn.text:
                                next_btn = btn
                                break
                            if not "Previous" in btn.text: # If only one and it's not Prev
                                next_btn = btn # risky but often true on page 1

                if next_btn and "href" in next_btn.attrs:
                    current_url = urljoin(base_url, next_btn["href"])
                    await asyncio.sleep(random.uniform(2, 4))
                else:
                    logger.info("No next page found on Flipkart.")
                    break

            await browser.close()

    def save_results(self):
        if not self.results:
            logger.warning("No data collected in this run.")
            return

        # Prepare Filenames
        clean_query = "".join(c for c in self.query if c.isalnum() or c in (' ', '_', '-')).replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        csv_filename = f"{clean_query}_{timestamp}.csv"
        json_filename = f"{clean_query}_{timestamp}.json"
        
        # Save CSV
        df = pd.DataFrame(self.results)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        logger.info(f"Saved CSV: {csv_filename}")
        
        # Save JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved JSON: {json_filename}")

# --- 4. Main Execution ---
async def run():
    parser = argparse.ArgumentParser(description="Amazon/Flipkart Multipage Scraper")
    parser.add_argument("--query", type=str, default="gaming laptops", help="Search query")
    parser.add_argument("--pages", type=int, default=3, help="Max pages per site (default: 3)")
    parser.add_argument("--headless", action='store_true', default=True, help="Headless mode")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Show browser")
    
    args = parser.parse_args()
    
    scraper = EcommerceScraper(query=args.query, max_pages=args.pages, headless=args.headless)
    
    # Run both sequentially to avoid rate limits flagging simultaneous traffic
    try:
        await scraper.scrape_amazon()
    except Exception as e:
        logger.error(f"Critical error in Amazon scrape: {e}")

    try:
        await scraper.scrape_flipkart()
    except Exception as e:
        logger.error(f"Critical error in Flipkart scrape: {e}")
        
    scraper.save_results()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user.")
