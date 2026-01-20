#!/usr/bin/env python3
"""Master CLI for all web scraping features."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ecommerce.tracker import EcommerceScraper
from src.jobs.scraper import JobScraper
from src.news.aggregator import NewsAggregator
from src.realestate.crawler import RealEstateCrawler
from src.common import setup_logger, get_config

config = get_config()
logger = setup_logger("MasterCLI", "scraper.log", 10 if config.debug else 20)


def create_parser():
    """Create argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Web Scraping Projects - Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all scrapers
  python scrape.py all
  
  # Run specific scrapers
  python scrape.py ecommerce --query "laptops" --pages 5
  python scrape.py jobs --role "python developer" --location "bangalore"
  python scrape.py news
  python scrape.py realestate --city "mumbai"
  
  # Run with visible browser
  python scrape.py ecommerce --query "phones" --no-headless
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Scraper to run")
    
    # All command
    parser_all = subparsers.add_parser("all", help="Run all scrapers")
    parser_all.add_argument("--headless", action="store_true", default=True,
                           help="Run in headless mode (default)")
    parser_all.add_argument("--no-headless", action="store_false", dest="headless",
                           help="Show browser windows")
    
    # E-commerce command
    parser_ecom = subparsers.add_parser("ecommerce", help="Run e-commerce price tracker")
    parser_ecom.add_argument("--query", type=str, default="gaming laptops",
                            help="Product search query (default: gaming laptops)")
    parser_ecom.add_argument("--pages", type=int, default=3,
                            help="Max pages per site (default: 3)")
    parser_ecom.add_argument("--headless", action="store_true", default=True,
                            help="Run in headless mode (default)")
    parser_ecom.add_argument("--no-headless", action="store_false", dest="headless",
                            help="Show browser window")
    
    # Jobs command
    parser_jobs = subparsers.add_parser("jobs", help="Run job portal scraper")
    parser_jobs.add_argument("--role", type=str, default="python developer",
                            help="Job role (default: python developer)")
    parser_jobs.add_argument("--location", type=str, default="remote",
                            help="Job location (default: remote)")
    parser_jobs.add_argument("--headless", action="store_true", default=True,
                            help="Run in headless mode (default)")
    parser_jobs.add_argument("--no-headless", action="store_false", dest="headless",
                            help="Show browser window")
    
    # News command
    parser_news = subparsers.add_parser("news", help="Run news headline aggregator")
    
    # Real estate command
    parser_real = subparsers.add_parser("realestate", help="Run real estate crawler")
    parser_real.add_argument("--city", type=str, default="pune",
                            help="City to search (default: pune)")
    parser_real.add_argument("--headless", action="store_true", default=True,
                            help="Run in headless mode (default)")
    parser_real.add_argument("--no-headless", action="store_false", dest="headless",
                            help="Show browser window")
    
    return parser


async def run_ecommerce(args):
    """Run e-commerce scraper."""
    logger.info("🛒 Starting E-commerce Price Tracker...")
    scraper = EcommerceScraper(
        query=args.query,
        max_pages=args.pages,
        headless=args.headless
    )
    
    try:
        await scraper.scrape_amazon()
    except Exception as e:
        logger.error(f"Amazon scrape failed: {e}")
    
    try:
        await scraper.scrape_flipkart()
    except Exception as e:
        logger.error(f"Flipkart scrape failed: {e}")
    
    scraper.save_results()
    logger.info("✓ E-commerce scraping complete\n")


async def run_jobs(args):
    """Run job scraper."""
    logger.info("💼 Starting Job Portal Scraper...")
    scraper = JobScraper(headless=args.headless)
    
    try:
        await scraper.scrape_naukri(args.role, args.location)
        scraper.save_data()
        logger.info("✓ Job scraping complete\n")
    except Exception as e:
        logger.error(f"Job scrape failed: {e}")


async def run_news():
    """Run news aggregator."""
    logger.info("📰 Starting News Headline Aggregator...")
    aggregator = NewsAggregator()
    
    try:
        await aggregator.run()
        aggregator.save_data()
        logger.info("✓ News aggregation complete\n")
    except Exception as e:
        logger.error(f"News aggregation failed: {e}")


async def run_realestate(args):
    """Run real estate crawler."""
    logger.info("🏠 Starting Real Estate Crawler...")
    crawler = RealEstateCrawler(headless=args.headless)
    
    try:
        await crawler.scrape_99acres(args.city)
        crawler.save_data()
        logger.info("✓ Real estate crawling complete\n")
    except Exception as e:
        logger.error(f"Real estate crawl failed: {e}")


async def run_all(args):
    """Run all scrapers sequentially."""
    logger.info("🚀 Starting ALL scrapers...\n")
    
    # Create default args for each scraper
    ecom_args = argparse.Namespace(
        query="gaming laptops",
        pages=2,
        headless=args.headless
    )
    jobs_args = argparse.Namespace(
        role="python developer",
        location="remote",
        headless=args.headless
    )
    real_args = argparse.Namespace(
        city="pune",
        headless=args.headless
    )
    
    # Run all scrapers
    await run_ecommerce(ecom_args)
    await run_jobs(jobs_args)
    await run_news()
    await run_realestate(real_args)
    
    logger.info("✓✓✓ ALL scrapers complete!")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "all":
            asyncio.run(run_all(args))
        elif args.command == "ecommerce":
            asyncio.run(run_ecommerce(args))
        elif args.command == "jobs":
            asyncio.run(run_jobs(args))
        elif args.command == "news":
            asyncio.run(run_news())
        elif args.command == "realestate":
            asyncio.run(run_realestate(args))
    except KeyboardInterrupt:
        logger.info("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=config.debug)
        sys.exit(1)


if __name__ == "__main__":
    main()
