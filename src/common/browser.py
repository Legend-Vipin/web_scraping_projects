"""Browser automation helpers and anti-detection utilities."""

import asyncio
import random
from typing import Optional
from playwright.async_api import Browser, Page, BrowserContext
from fake_useragent import UserAgent

from .logger import get_logger

logger = get_logger(__name__)
ua = UserAgent()


async def get_stealth_context(
    browser: Browser,
    locale: str = 'en-IN',
    timezone: str = 'Asia/Kolkata'
) -> BrowserContext:
    """
    Create a browser context with anti-detection measures.
    
    Args:
        browser: Playwright browser instance
        locale: Browser locale (default: 'en-IN')
        timezone: Browser timezone (default: 'Asia/Kolkata')
    
    Returns:
        Configured browser context
    """
    # Randomize viewport to avoid fingerprinting
    width = random.randint(1366, 1920)
    height = random.randint(768, 1080)
    
    try:
        user_agent = ua.random
    except Exception:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    context = await browser.new_context(
        user_agent=user_agent,
        viewport={'width': width, 'height': height},
        locale=locale,
        timezone_id=timezone,
        java_script_enabled=True,
        accept_downloads=False,
        # Additional anti-detection
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
        }
    )
    
    # Anti-detection scripts
    await context.add_init_script("""
        // Override navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Override chrome property
        window.chrome = {
            runtime: {}
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    logger.debug(f"Created stealth context with viewport {width}x{height}")
    return context


async def safe_goto(
    page: Page,
    url: str,
    timeout: int = 60000,
    wait_until: str = "domcontentloaded",
    block_images: bool = True,
    delay_range: tuple = (2.0, 5.0)
) -> bool:
    """
    Safely navigate to a URL with error handling and anti-detection delays.
    
    Args:
        page: Playwright page instance
        url: URL to navigate to
        timeout: Navigation timeout in milliseconds (default: 60000)
        wait_until: When to consider navigation succeeded (default: "domcontentloaded")
        block_images: Whether to block image loading for speed (default: True)
        delay_range: Random delay range in seconds after navigation (default: 2-5s)
    
    Returns:
        True if navigation succeeded, False otherwise
    """
    try:
        logger.info(f"Navigating to: {url}")
        
        # Block images and other heavy resources to speed up loading
        if block_images:
            await page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,ico}",
                lambda route: route.abort()
            )
        
        await page.goto(url, wait_until=wait_until, timeout=timeout)
        
        # Random delay to mimic human behavior
        delay = random.uniform(*delay_range)
        logger.debug(f"Waiting {delay:.2f}s after page load")
        await asyncio.sleep(delay)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load {url}: {e}")
        return False


async def auto_scroll(
    page: Page,
    max_scrolls: int = 5,
    scroll_distance: int = 600,
    delay_range: tuple = (0.5, 1.5)
) -> None:
    """
    Gradually scroll the page to trigger lazy loading.
    
    Args:
        page: Playwright page instance
        max_scrolls: Maximum number of scroll iterations (default: 5)
        scroll_distance: Pixels to scroll per iteration (default: 600)
        delay_range: Random delay range between scrolls in seconds (default: 0.5-1.5s)
    """
    try:
        logger.debug("Auto-scrolling page to trigger lazy loading")
        prev_height = -1
        
        for i in range(max_scrolls):
            # Scroll down
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            
            # Random delay between scrolls
            delay = random.uniform(*delay_range)
            await asyncio.sleep(delay)
            
            # Check if we've reached the bottom
            curr_height = await page.evaluate("document.body.scrollHeight")
            if curr_height == prev_height:
                logger.debug(f"Reached page bottom after {i+1} scrolls")
                break
            prev_height = curr_height
            
    except Exception as e:
        logger.warning(f"Auto-scroll warning: {e}")


async def handle_popups(page: Page) -> None:
    """
    Dismiss common popups and modals.
    
    Args:
        page: Playwright page instance
    """
    try:
        # Common close button selectors
        close_selectors = [
            "button[aria-label*='close' i]",
            "button[class*='close' i]",
            ".modal-close",
            ".popup-close",
            "[data-dismiss='modal']"
        ]
        
        for selector in close_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    logger.debug(f"Closed popup using selector: {selector}")
                    await asyncio.sleep(0.5)
            except Exception:
                continue
                
    except Exception as e:
        logger.debug(f"Popup handling: {e}")
