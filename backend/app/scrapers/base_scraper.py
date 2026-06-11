import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    STANDARD_FIELDS = ["platform", "author", "content", "time", "likes", "comments", "tags"]

    def __init__(self):
        self.name = self.__class__.__name__
        self.platform = ""
        self._setup_logging()

    def _setup_logging(self):
        self.logger = logging.getLogger(self.name)

    def _get_headers(self) -> Dict[str, str]:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        time.sleep(random.uniform(min_sec, max_sec))

    def _validate_result(self, item: Dict) -> bool:
        for field in self.STANDARD_FIELDS:
            if field not in item:
                item[field] = None
        return item.get("content") is not None

    def _create_standard_item(self, **kwargs) -> Dict:
        item = {
            "platform": kwargs.get("platform", self.platform),
            "author": kwargs.get("author", ""),
            "content": kwargs.get("content", ""),
            "time": kwargs.get("time", ""),
            "likes": kwargs.get("likes", 0),
            "comments": kwargs.get("comments", 0),
            "tags": kwargs.get("tags", [])
        }
        return item

    @abstractmethod
    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        """
        Scrape data for given keyword.

        Args:
            keyword: Search keyword
            max_count: Maximum number of results to return

        Returns:
            List of dictionaries with standardized fields:
            {platform, author, content, time, likes, comments, tags}
        """
        pass

    def scrape_with_retry(self, keyword: str, max_count: int = 100, max_retries: int = 3) -> List[Dict]:
        """
        Scrape with automatic retry on failure.
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Scraping attempt {attempt + 1}/{max_retries} for keyword: {keyword}")
                results = self.scrape(keyword, max_count)
                valid_results = [r for r in results if self._validate_result(r)]
                self.logger.info(f"Successfully scraped {len(valid_results)} items")
                return valid_results
            except Exception as e:
                last_error = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    self._random_delay(2, 5)

        self.logger.error(f"All {max_retries} attempts failed. Last error: {last_error}")
        return []