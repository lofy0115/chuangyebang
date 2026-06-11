import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import time
from datetime import datetime

from .base_scraper import BaseScraper


class WeiboScraper(BaseScraper):
    PLATFORM_NAME = "微博"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.session = requests.Session()
        self.base_url = "https://s.weibo.com"
        self.headers = self._get_headers()
        self.headers["Referer"] = "https://weibo.com"

    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                self._random_delay(2, 5)
                response = self.session.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 418:
                    self.logger.warning(f"Got 418, proxy blocked. Attempt {attempt + 1}")
                    time.sleep(30)
                elif response.status_code == 403:
                    self.logger.warning(f"Access forbidden. Attempt {attempt + 1}")
            except requests.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
        return None

    def _parse_count(self, count_str: str) -> int:
        if not count_str:
            return 0
        count_str = count_str.strip()
        if '万' in count_str:
            return int(float(count_str.replace('万', '')) * 10000)
        elif '亿' in count_str:
            return int(float(count_str.replace('亿', '')) * 100000000)
        try:
            return int(count_str)
        except ValueError:
            return 0

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        page = 1
        max_pages = (max_count // 20) + 1

        while len(results) < max_count and page <= max_pages:
            url = f"{self.base_url}/weibo"
            params = {
                "q": keyword,
                "typeall": 1,
                "suball": 1,
                "timescope": "custom:2024-01-01:2025-12-31",
                "Refer": "g",
                "page": page
            }

            self.logger.info(f"Scraping Weibo page {page} for keyword: {keyword}")
            html = self._make_request(url, params)

            if not html:
                self.logger.warning(f"Failed to fetch page {page}, trying next")
                page += 1
                continue

            items = self._parse_page(html, keyword)
            if not items:
                self.logger.info(f"No more results on page {page}")
                break

            results.extend(items)
            self.logger.info(f"Page {page}: got {len(items)} items, total: {len(results)}")
            page += 1

            if page <= max_pages:
                self._random_delay(3, 7)

        return results[:max_count]

    def _parse_page(self, html: str, keyword: str) -> List[Dict]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            for item in soup.select("div[mid]"):
                try:
                    content_elem = item.select_one("div.content")
                    if not content_elem:
                        continue

                    content = content_elem.get_text(separator=" ", strip=True)
                    if len(content) < 10:
                        continue

                    user_elem = item.select_one("a.name")
                    author = user_elem.get_text(strip=True) if user_elem else "未知用户"

                    time_elem = item.select_one("div.info a[data-date]")
                    post_time = time_elem.get("data-date", "") if time_elem else ""

                    likes_elem = item.select_one("a[data-btn-like]")
                    likes = self._parse_count(likes_elem.get_text(strip=True) if likes_elem else "0")

                    comments_elem = item.select_one("a[data-btn-comment]")
                    comments = self._parse_count(comments_elem.get_text(strip=True) if comments_elem else "0")

                    repost_elem = item.select_one("a[data-btn-repost]")
                    reposts = self._parse_count(repost_elem.get_text(strip=True) if repost_elem else "0")

                    result = self._create_standard_item(
                        platform=self.platform,
                        author=author,
                        content=content,
                        time=post_time,
                        likes=likes,
                        comments=comments,
                        tags=[keyword, "微博"]
                    )
                    results.append(result)

                except Exception as e:
                    self.logger.debug(f"Error parsing item: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing page: {str(e)}")

        return results


class WeiboHotSearchScraper(WeiboScraper):
    PLATFORM_NAME = "微博热搜"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.hot_url = "https://s.weibo.com/top/summary"

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        try:
            html = self._make_request(self.hot_url)
            if not html:
                return self._fallback_to_mock(keyword, max_count)

            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("tr")[:max_count]:
                rank_elem = item.select_one(".rank_top")
                title_elem = item.select_one(".title")
                hot_elem = item.select_one(".hot_rank")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if keyword in title or not keyword:
                        results.append(self._create_standard_item(
                            platform=self.platform,
                            author="微博热搜",
                            content=title,
                            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                            likes=self._parse_count(hot_elem.get_text(strip=True) if hot_elem else "0"),
                            comments=0,
                            tags=["热搜", title]
                        ))
        except Exception as e:
            self.logger.error(f"Hot search scrape error: {str(e)}")

        if not results:
            return self._fallback_to_mock(keyword, max_count)
        return results[:max_count]

    def _fallback_to_mock(self, keyword: str, max_count: int) -> List[Dict]:
        self.logger.info("Using mock data for Weibo hot search")
        return [
            self._create_standard_item(
                platform=self.platform,
                author="微博热搜",
                content=f"热搜话题{i} - {keyword}",
                time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                likes=10000 - i * 100,
                comments=500 - i * 10,
                tags=[keyword, "热搜"]
            )
            for i in range(min(max_count, 20))
        ]