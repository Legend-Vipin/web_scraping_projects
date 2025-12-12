import asyncio
import httpx
import logging
import sys
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('aggregator.log')
    ]
)
logger = logging.getLogger(__name__)

class NewsAggregator:
    def __init__(self):
        self.data: List[Dict] = []
        self.ua = UserAgent()
        
    def _get_headers(self):
        try:
            ua_str = self.ua.random
        except:
            ua_str = "Mozilla/5.0"
        return {"User-Agent": ua_str}

    async def scrape_toi(self, client: httpx.AsyncClient):
        url = "https://timesofindia.indiatimes.com/home/headlines"
        try:
            resp = await client.get(url, headers=self._get_headers())
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                # TOI headlines usually in span.w_tle
                headlines = soup.select("span.w_tle > a") or soup.select(".main-content a")
                count = 0
                for h in headlines:
                    text = h.get_text(strip=True)
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
                logger.info(f"TOI: Collected {count} headlines.")
            else:
                logger.error(f"TOI failed: {resp.status_code}")
        except Exception as e:
            logger.error(f"TOI error: {e}")

    async def scrape_hindu(self, client: httpx.AsyncClient):
        url = "https://www.thehindu.com/"
        try:
            resp = await client.get(url, headers=self._get_headers())
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                # The Hindu title class often just 'title' or in h3 a
                headlines = soup.select("h3.title a") or soup.select(".story-card-news h3 a")
                count = 0
                for h in headlines:
                    text = h.get_text(strip=True)
                    link = h.get('href', '')
                    if text and link:
                        self.data.append({
                            "source": "The Hindu",
                            "headline": text,
                            "link": link,
                            "timestamp": datetime.now().isoformat()
                        })
                        count += 1
                logger.info(f"The Hindu: Collected {count} headlines.")
            else:
                logger.error(f"The Hindu failed: {resp.status_code}")
        except Exception as e:
            logger.error(f"The Hindu error: {e}")

    async def scrape_ndtv(self, client: httpx.AsyncClient):
        url = "https://www.ndtv.com/top-stories"
        try:
            resp = await client.get(url, headers=self._get_headers())
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'lxml')
                # NDTV news_Itm-cont
                headlines = soup.select(".news_Itm-cont h2 a")
                count = 0
                for h in headlines:
                    text = h.get_text(strip=True)
                    link = h.get('href', '')
                    if text and link:
                        self.data.append({
                            "source": "NDTV",
                            "headline": text,
                            "link": link,
                            "timestamp": datetime.now().isoformat()
                        })
                        count += 1
                logger.info(f"NDTV: Collected {count} headlines.")
            else:
                logger.error(f"NDTV failed: {resp.status_code}")
        except Exception as e:
            logger.error(f"NDTV error: {e}")

    async def run(self):
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            await asyncio.gather(
                self.scrape_toi(client),
                self.scrape_hindu(client),
                self.scrape_ndtv(client)
            )

    def save_data(self):
        if not self.data:
            logger.warning("No data collected.")
            return

        df = pd.DataFrame(self.data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"headlines_{timestamp}.csv"
        json_file = f"headlines_{timestamp}.json"
        
        df.to_csv(csv_file, index=False)
        df.to_json(json_file, orient='records', indent=2)
        logger.info(f"Saved {len(df)} headlines to {csv_file}")

def main():
    aggregator = NewsAggregator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(aggregator.run())
    except Exception as e:
        logger.error(f"Aggregation failed: {e}")
    
    aggregator.save_data()

if __name__ == "__main__":
    main()
