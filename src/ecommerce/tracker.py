"""E-commerce price tracker for Amazon and Flipkart with async support."""

import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page

# Import common utilities
from src.common import (
    setup_logger,
    get_config,
    get_stealth_context,
    safe_goto,
    auto_scroll,
    clean_price,
    extract_text,
    extract_attr,
    validate_product_data,
    filter_valid_data,
)

# Configuration
config = get_config()

# Setup logger
logger = setup_logger(
    name="EcommerceTracker",
    log_file="ecommerce_tracker.log",
    level=10 if config.debug else 20
)


class Product:
    """Product data structure."""
    
    def __init__(
        self,
        platform: str,
        title: str,
        price: Optional[int],
        rating: Optional[str],
        reviews: Optional[str],
        url: str,
        image_url: Optional[str],
        availability: str
    ):
        self.platform = platform
        self.title = title
        self.price = price
        self.rating = rating
        self.reviews = reviews
        self.url = url
        self.image_url = image_url
        self.availability = availability
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert product to dictionary."""
        return self.__dict__


class EcommerceScraper:
    """E-commerce scraper for Amazon and Flipkart."""
    
    def __init__(self, query: str, max_pages: int = 5, headless: bool = True):
        self.query = query
        self.max_pages = max_pages
        self.headless = headless
        self.results: List[Dict] = []
        self.seen_urls = set()

    async def scrape_amazon(self) -> None:
        """Scrape Amazon India for products."""
        logger.info(f"--- Starting Amazon Scrape: '{self.query}' ---")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await get_stealth_context(browser)
            page = await context.new_page()

            base_url = "https://www.amazon.in"
            search_url = f"{base_url}/s?k={self.query.replace(' ', '+')}"
            current_url = search_url

            try:
                for page_num in range(1, self.max_pages + 1):
                    logger.info(f"Processing Amazon Page {page_num}...")

                    if not await safe_goto(page, current_url, block_images=True):
                        break

                    await auto_scroll(page)

                    content = await page.content()
                    soup = BeautifulSoup(content, 'lxml')

                    # Check for CAPTCHA/blocking
                    if "Enter the characters you see below" in soup.text:
                        logger.error("Amazon CAPTCHA detected! Aborting Amazon scrape.")
                        break

                    # Find product containers
                    containers = soup.select("div[data-component-type='s-search-result']")
                    if not containers:
                        logger.warning(f"No items found on page {page_num}.")
                        break

                    new_items = 0
                    for item in containers:
                        try:
                            title = extract_text(
                                item,
                                ["h2 a span", "h2", "span.a-text-normal"]
                            )
                            if not title:
                                continue

                            # Get product URL
                            link_suffix = extract_attr(
                                item,
                                ["h2 a", "a.a-link-normal"],
                                "href"
                            )
                            if not link_suffix:
                                continue
                            
                            url = urljoin(base_url, link_suffix)

                            # Skip duplicates
                            unique_key = f"Amazon_{url}"
                            if unique_key in self.seen_urls:
                                continue
                            self.seen_urls.add(unique_key)

                            # Extract price
                            price_raw = extract_text(
                                item,
                                ["span.a-price-whole", "span.a-offscreen"]
                            )
                            price = clean_price(price_raw)

                            # Extract rating
                            rating = extract_text(
                                item,
                                ["span.a-icon-alt", "i.a-icon-star-small"]
                            )
                            if rating:
                                rating = rating.split(' ')[0]

                            # Extract reviews
                            reviews = extract_text(
                                item,
                                ["span.a-size-base.s-underline-text", "span.a-size-base"]
                            )

                            # Extract image
                            img_url = extract_attr(item, ["img.s-image"], "src")

                            # Determine availability
                            availability = "In Stock" if price else "Out of Stock"
                            avail_text = extract_text(item, ["span.a-color-price"]) or ""
                            if "Currently unavailable" in avail_text:
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
                            logger.warning(f"Error parsing Amazon item: {e}")
                            continue

                    logger.info(f"Page {page_num}: Extracted {new_items} items.")

                    # Find next page
                    next_btn = soup.select_one("a.s-pagination-next")
                    if next_btn and "href" in next_btn.attrs:
                        current_url = urljoin(base_url, next_btn["href"])
                        await asyncio.sleep(config.request_delay_max)
                    else:
                        logger.info("No next page found on Amazon.")
                        break

            finally:
                await browser.close()

    async def scrape_flipkart(self) -> None:
        """Scrape Flipkart for products."""
        logger.info(f"--- Starting Flipkart Scrape: '{self.query}' ---")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await get_stealth_context(browser)
            page = await context.new_page()

            base_url = "https://www.flipkart.com"
            search_url = f"{base_url}/search?q={self.query.replace(' ', '%20')}&sort=recency_desc"
            current_url = search_url

            try:
                for page_num in range(1, self.max_pages + 1):
                    logger.info(f"Processing Flipkart Page {page_num}...")

                    if not await safe_goto(page, current_url, block_images=True):
                        break

                    await auto_scroll(page)

                    content = await page.content()
                    soup = BeautifulSoup(content, 'lxml')

                    # Find product containers (multiple possible layouts)
                    containers = (
                        soup.select("div._1AtVbE") +
                        soup.select("div._75nlfW") +
                        soup.select("div[data-id]")
                    )

                    # Filter valid containers
                    valid_containers = [c for c in containers if c.select_one("a[href]")]

                    if not valid_containers:
                        logger.warning(f"No items found on page {page_num}.")
                        break

                    new_items = 0
                    for item in valid_containers:
                        try:
                            # Extract title
                            title = extract_text(
                                item,
                                ["div.KzDlHZ", "div._4rR01T", "a.s1Q9rs", "div.name"]
                            )
                            
                            # Fallback: get text from link
                            if not title:
                                link = item.select_one("a[href]")
                                if link:
                                    title = link.get_text(strip=True)

                            if not title:
                                continue

                            # Get product URL
                            link_suffix = extract_attr(
                                item,
                                ["a.CGtC98", "a._1fQZEK", "a.s1Q9rs", "a[href]"],
                                "href"
                            )
                            if not link_suffix:
                                continue
                            
                            url = urljoin(base_url, link_suffix)

                            # Skip duplicates
                            unique_key = f"Flipkart_{url}"
                            if unique_key in self.seen_urls:
                                continue
                            self.seen_urls.add(unique_key)

                            # Extract price
                            price_raw = extract_text(
                                item,
                                ["div.Nx9bqj", "div._30jeq3", "div._25b18c ._30jeq3"]
                            )
                            price = clean_price(price_raw)

                            # Extract rating
                            rating = extract_text(item, ["div.XQDdHH", "div._3LWZlK"])

                            # Extract reviews
                            reviews = extract_text(item, ["span.Wphh3N", "span._2_R_DZ"])

                            # Extract image
                            img_url = extract_attr(item, ["img._396cs4", "img"], "src")

                            # Determine availability
                            availability = "In Stock" if price else "Out of Stock"
                            avail_text = extract_text(item, ["div._3Owiq+"]) or ""
                            if "Sold Out" in avail_text:
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
                            logger.warning(f"Error parsing Flipkart item: {e}")
                            continue

                    logger.info(f"Page {page_num}: Extracted {new_items} items.")

                    # Find next page
                    next_btn = soup.find('a', string="Next")
                    if not next_btn:
                        next_btns = soup.select("a._1LKTO3")
                        for btn in next_btns:
                            if "Next" in btn.text:
                                next_btn = btn
                                break

                    if next_btn and "href" in next_btn.attrs:
                        current_url = urljoin(base_url, next_btn["href"])
                        await asyncio.sleep(config.request_delay_max)
                    else:
                        logger.info("No next page found on Flipkart.")
                        break

            finally:
                await browser.close()

    def save_results(self) -> None:
        """Save collected data with validation."""
        if not self.results:
            logger.warning("No data collected in this run.")
            return

        # Validate and filter data
        valid_data = filter_valid_data(self.results, validate_product_data)
        invalid_count = len(self.results) - len(valid_data)

        if invalid_count > 0:
            logger.warning(f"Filtered out {invalid_count} invalid entries")

        if not valid_data:
            logger.warning("No valid data to save")
            return

        # Generate filenames
        clean_query = "".join(
            c for c in self.query
            if c.isalnum() or c in (' ', '_', '-')
        ).replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_file = config.data_dir / f"{clean_query}_{timestamp}.csv"
        json_file = config.data_dir / f"{clean_query}_{timestamp}.json"

        # Save based on output format setting
        df = pd.DataFrame(valid_data)

        if config.output_format in ["csv", "both"]:
            df.to_csv(csv_file, index=False, encoding='utf-8')
            logger.info(f"Saved {len(df)} products to {csv_file}")

        if config.output_format in ["json", "both"]:
            df.to_json(json_file, orient='records', indent=2)
            logger.info(f"Saved {len(df)} products to {json_file}")


async def run() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Amazon/Flipkart E-commerce Price Tracker"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="gaming laptops",
        help="Search query"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Max pages per site (default: 3)"
    )
    parser.add_argument(
        "--headless",
        action='store_true',
        default=True,
        help="Headless mode (default)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Show browser"
    )

    args = parser.parse_args()

    scraper = EcommerceScraper(
        query=args.query,
        max_pages=args.pages,
        headless=args.headless
    )

    # Run scrapers sequentially to avoid rate limits
    try:
        await scraper.scrape_amazon()
    except Exception as e:
        logger.error(f"Critical error in Amazon scrape: {e}", exc_info=config.debug)

    try:
        await scraper.scrape_flipkart()
    except Exception as e:
        logger.error(f"Critical error in Flipkart scrape: {e}", exc_info=config.debug)

    scraper.save_results()


def main():
    """CLI entry point."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user.")


if __name__ == "__main__":
    main()
