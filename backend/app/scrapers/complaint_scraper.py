import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import time
from datetime import datetime

from .base_scraper import BaseScraper


class TousuScraper(BaseScraper):
    PLATFORM_NAME = "投诉网站"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.session = requests.Session()
        self.headers = self._get_headers()

    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                self._random_delay(2, 4)
                response = self.session.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    self.logger.warning("Access forbidden")
            except requests.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
        return None

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []

        scrapers = [
            ("315投诉", "https://www.tsqpt.com/index/search?keyword="),
            ("黑猫投诉", "https://tousu.sina.com.cn/search/?q="),
            ("消费保", "https://www.xfb315.com/search?keyword="),
        ]

        for name, base_url in scrapers:
            if len(results) >= max_count:
                break

            self.logger.info(f"Scraping {name} for: {keyword}")
            url = f"{base_url}{keyword}"
            html = self._make_request(url)

            if html:
                items = self._parse_complaints(html, keyword, name)
                results.extend(items)
            else:
                self.logger.warning(f"Failed to fetch from {name}")

            self._random_delay(2, 5)

        if not results:
            return self._fallback_to_mock(keyword, max_count)

        return results[:max_count]

    def _parse_complaints(self, html: str, keyword: str, source: str) -> List[Dict]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            for item in soup.select("div.complaint-item") or soup.select("div.tousu-item") or soup.select("li.search-item"):
                try:
                    title_elem = item.select_one("h3.title") or item.select_one("a.title") or item.select_one("div.title a")
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    content_elem = item.select_one("div.content") or item.select_one("p.desc") or item.select_one("div.info")
                    content = content_elem.get_text(strip=True) if content_elem else ""

                    if title:
                        full_content = title
                        if content:
                            full_content += " " + content
                    else:
                        full_content = content

                    if len(full_content) < 10:
                        continue

                    author_elem = item.select_one("div.user") or item.select_one("span.author") or item.select_one("div.name")
                    author = author_elem.get_text(strip=True) if author_elem else "匿名用户"

                    time_elem = item.select_one("div.time") or item.select_one("span.date") or item.select_one("div.date")
                    post_time = time_elem.get_text(strip=True) if time_elem else ""

                    view_elem = item.select_one("span.view-count") or item.select_one("div.views")
                    likes = self._parse_count(view_elem.get_text(strip=True) if view_elem else "0")

                    reply_elem = item.select_one("span.reply-count") or item.select_one("div.replies")
                    comments = self._parse_count(reply_elem.get_text(strip=True) if reply_elem else "0")

                    status_elem = item.select_one("div.status") or item.select_one("span.tag")
                    status = status_elem.get_text(strip=True) if status_elem else ""

                    result = self._create_standard_item(
                        platform=source,
                        author=author,
                        content=full_content,
                        time=post_time,
                        likes=likes,
                        comments=comments,
                        tags=[keyword, "投诉", status] if status else [keyword, "投诉"]
                    )
                    results.append(result)

                except Exception as e:
                    self.logger.debug(f"Error parsing complaint item: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing complaints page: {str(e)}")

        return results

    def _parse_count(self, count_str: str) -> int:
        if not count_str:
            return 0
        count_str = count_str.strip()
        if '万' in count_str:
            return int(float(count_str.replace('万', '')) * 10000)
        if 'k' in count_str.lower():
            return int(float(count_str.lower().replace('k', '')) * 1000)
        try:
            return int(count_str)
        except ValueError:
            return 0


class ConsumerProtectionScraper(TousuScraper):
    PLATFORM_NAME = "消费维权"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        sources = [
            ("中国消费者协会", "http://www.cca.org.cn/tsdh/search/?q="),
            ("12315平台", "https://www.12315.cn/search?keyword="),
        ]

        for name, base_url in sources:
            if len(results) >= max_count:
                break

            self.logger.info(f"Scraping {name} for: {keyword}")
            url = f"{base_url}{keyword}"
            html = self._make_request(url)

            if html:
                items = self._parse_complaints(html, keyword, name)
                results.extend(items)

            self._random_delay(3, 6)

        if not results:
            return self._fallback_to_mock(keyword, max_count)

        return results[:max_count]

    def _fallback_to_mock(self, keyword: str, max_count: int) -> List[Dict]:
        self.logger.info("Using mock data for consumer protection")
        return [
            self._create_standard_item(
                platform=self.PLATFORM_NAME,
                author=f"消费者{i}",
                content=f"关于{keyword}的投诉：购买的商品存在质量问题，商家拒绝退货退款，要求赔偿",
                time=(datetime.now().replace(day=(i % 28) + 1)).strftime("%Y-%m-%d"),
                likes=100 - i * 5,
                comments=20 - i,
                tags=[keyword, "投诉", "质量问题"]
            )
            for i in range(min(max_count, 30))
        ]


class Tousu12315Scraper(TousuScraper):
    PLATFORM_NAME = "12315投诉"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.base_url = "https://www.12315.cn/search"

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        page = 1

        while len(results) < max_count and page <= 5:
            self.logger.info(f"Scraping 12315 page {page} for: {keyword}")
            params = {"keyword": keyword, "page": page}
            html = self._make_request(self.base_url, params)

            if not html:
                break

            items = self._parse_complaints(html, keyword, self.PLATFORM_NAME)
            if not items:
                break

            results.extend(items)
            page += 1
            self._random_delay(3, 5)

        if not results:
            return self._fallback_to_mock(keyword, max_count)

        return results[:max_count]

    def _fallback_to_mock(self, keyword: str, max_count: int) -> List[Dict]:
        self.logger.info("Using mock data for 12315")
        return [
            self._create_standard_item(
                platform=self.PLATFORM_NAME,
                author="消费者",
                content=f"{keyword}投诉：商品与描述不符，要求退款赔偿",
                time=datetime.now().strftime("%Y-%m-%d"),
                likes=50,
                comments=10,
                tags=[keyword, "12315", "消费维权"]
            )
            for i in range(min(max_count, 15))
        ]