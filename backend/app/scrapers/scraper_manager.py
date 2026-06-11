import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

from .base_scraper import BaseScraper
from .weibo_scraper import WeiboScraper, WeiboHotSearchScraper
from .xiaohongshu_scraper import XiaohongshuScraper, XiaohongshuNoteScraper
from .ecommerce_scraper import JDCommentScraper, TaobaoCommentScraper, EcommerceCommentScraper
from .complaint_scraper import TousuScraper, ConsumerProtectionScraper, Tousu12315Scraper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScraperManager:
    SCRAPERS = {
        "weibo": WeiboScraper,
        "weibo_hot": WeiboHotSearchScraper,
        "xiaohongshu": XiaohongshuScraper,
        "xiaohongshu_note": XiaohongshuNoteScraper,
        "jd": JDCommentScraper,
        "taobao": TaobaoCommentScraper,
        "ecommerce": EcommerceCommentScraper,
        "tousu": TousuScraper,
        "consumer_protection": ConsumerProtectionScraper,
        "12315": Tousu12315Scraper,
    }

    PLATFORM_NAMES = {
        "weibo": "微博",
        "weibo_hot": "微博热搜",
        "xiaohongshu": "小红书",
        "xiaohongshu_note": "小红书笔记",
        "jd": "京东",
        "taobao": "淘宝",
        "ecommerce": "电商评论",
        "tousu": "投诉网站",
        "consumer_protection": "消费维权",
        "12315": "12315投诉",
    }

    def __init__(self):
        self.logger = logger
        self._init_scrapers()

    def _init_scrapers(self):
        self.scrapers = {}
        for name, scraper_class in self.SCRAPERS.items():
            try:
                self.scrapers[name] = scraper_class()
                self.logger.info(f"Initialized scraper: {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name}: {str(e)}")

    def scrape(
        self,
        keyword: str,
        platforms: Optional[List[str]] = None,
        max_count: int = 100,
        parallel: bool = True
    ) -> List[Dict]:
        """
        Scrape data from multiple platforms.

        Args:
            keyword: Search keyword
            platforms: List of platform names to scrape (None = all)
            max_count: Maximum total results
            parallel: Whether to run scrapers in parallel

        Returns:
            List of standardized result dictionaries
        """
        if platforms is None:
            platforms = list(self.SCRAPERS.keys())

        results = []

        if parallel and len(platforms) > 1:
            results = self._scrape_parallel(keyword, platforms, max_count)
        else:
            results = self._scrape_sequential(keyword, platforms, max_count)

        self.logger.info(f"Total scraped: {len(results)} items from {len(platforms)} platforms")
        return results

    def _scrape_parallel(self, keyword: str, platforms: List[str], max_count: int) -> List[Dict]:
        results = []
        per_platform = (max_count // len(platforms)) + 10

        with ThreadPoolExecutor(max_workers=min(len(platforms), 5)) as executor:
            future_to_platform = {}
            for platform in platforms:
                if platform in self.scrapers:
                    future = executor.submit(self._scrape_single, platform, keyword, per_platform)
                    future_to_platform[future] = platform

            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    items = future.result()
                    results.extend(items)
                    self.logger.info(f"{platform}: got {len(items)} items")
                except Exception as e:
                    self.logger.error(f"{platform} failed: {str(e)}")

        return results

    def _scrape_sequential(self, keyword: str, platforms: List[str], max_count: int) -> List[Dict]:
        results = []
        per_platform = (max_count // len(platforms)) + 10

        for platform in platforms:
            if platform not in self.scrapers:
                self.logger.warning(f"Unknown platform: {platform}")
                continue

            try:
                items = self._scrape_single(platform, keyword, per_platform)
                results.extend(items)
                self.logger.info(f"{platform}: got {len(items)} items")
            except Exception as e:
                self.logger.error(f"{platform} failed: {str(e)}")

        return results

    def _scrape_single(self, platform: str, keyword: str, max_count: int) -> List[Dict]:
        scraper = self.scrapers.get(platform)
        if not scraper:
            return []

        try:
            return scraper.scrape_with_retry(keyword, max_count, max_retries=2)
        except Exception as e:
            self.logger.error(f"Scraper {platform} error: {str(e)}")
            return []

    def get_platforms(self) -> List[str]:
        return list(self.SCRAPERS.keys())

    def get_platform_name(self, platform: str) -> str:
        return self.PLATFORM_NAMES.get(platform, platform)

    def scrape_all(self, keyword: str, max_count: int = 100) -> List[Dict]:
        return self.scrape(keyword, platforms=None, max_count=max_count, parallel=True)

    def scrape_by_category(self, keyword: str, category: str, max_count: int = 100) -> List[Dict]:
        categories = {
            "social": ["weibo", "weibo_hot", "xiaohongshu", "xiaohongshu_note"],
            "ecommerce": ["jd", "taobao", "ecommerce"],
            "complaint": ["tousu", "consumer_protection", "12315"],
        }

        platforms = categories.get(category, [])
        if not platforms:
            self.logger.warning(f"Unknown category: {category}")
            return []

        return self.scrape(keyword, platforms=platforms, max_count=max_count)

    def stats(self) -> Dict:
        return {
            "total_scrapers": len(self.scrapers),
            "platforms": self.get_platforms(),
            "timestamp": datetime.now().isoformat()
        }


class ScraperFactory:
    @staticmethod
    def create(platform: str) -> Optional[BaseScraper]:
        if platform in ScraperManager.SCRAPERS:
            return ScraperManager.SCRAPERS[platform]()
        return None

    @staticmethod
    def create_all() -> Dict[str, BaseScraper]:
        return {name: cls() for name, cls in ScraperManager.SCRAPERS.items()}


if __name__ == "__main__":
    manager = ScraperManager()
    print("Available platforms:", manager.get_platforms())

    test_keyword = "手机"
    print(f"\nTesting scrape for keyword: {test_keyword}")

    results = manager.scrape(test_keyword, platforms=["weibo", "xiaohongshu"], max_count=10)
    print(f"Got {len(results)} results")

    for r in results[:3]:
        print(f"  [{r['platform']}] {r['author']}: {r['content'][:50]}...")