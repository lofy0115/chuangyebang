import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import time
from datetime import datetime

from .base_scraper import BaseScraper


class JDCommentScraper(BaseScraper):
    PLATFORM_NAME = "京东"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.session = requests.Session()
        self.headers = self._get_headers()
        self.headers["Referer"] = "https://www.jd.com"

    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                self._random_delay(2, 5)
                response = self.session.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    self.logger.warning("JD access forbidden")
            except requests.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
        return None

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        page = 1
        page_size = 20

        search_url = f"https://search.jd.com/Search?keyword={keyword}&enc=utf-8"
        html = self._make_request(search_url)

        if not html:
            return self._fallback_to_mock(keyword, max_count)

        product_ids = self._extract_product_ids(html)

        for pid in product_ids[:10]:
            if len(results) >= max_count:
                break

            comments_url = f"https://item.jd.com/{pid}.html"
            comments_html = self._make_request(comments_url)

            if comments_html:
                items = self._parse_comments(comments_html, keyword)
                results.extend(items)

            self._random_delay(3, 6)

        if not results:
            return self._fallback_to_mock(keyword, max_count)

        return results[:max_count]

    def _extract_product_ids(self, html: str) -> List[str]:
        ids = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("div.gl-i-wrap") or soup.select("div[data-sku]"):
                sku = item.get("data-sku") or item.select_one("a[href*='/product/']")
                if sku:
                    ids.append(str(sku))
        except Exception as e:
            self.logger.debug(f"Error extracting product IDs: {str(e)}")
        return ids[:20]

    def _parse_comments(self, html: str, keyword: str) -> List[Dict]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            for comment in soup.select("div.comment-item") or soup.select("div[data-comment-id]"):
                try:
                    content_elem = comment.select_one("div.comment-text") or comment.select_one("p.comment-con")
                    content = content_elem.get_text(strip=True) if content_elem else ""

                    if len(content) < 5:
                        continue

                    author_elem = comment.select_one("div.user-info") or comment.select_one("span.username")
                    author = author_elem.get_text(strip=True) if author_elem else "京东用户"

                    time_elem = comment.select_one("div.comment-time") or comment.select_one("span.date")
                    post_time = time_elem.get_text(strip=True) if time_elem else ""

                    star_elem = comment.select_one("div.star") or comment.select_one("span.star")
                    rating = 5
                    if star_elem:
                        star_class = star_elem.get("class", [])
                        for cls in star_class:
                            if "star" in cls.lower():
                                try:
                                    rating = int(re.search(r'\d', cls).group())
                                except:
                                    pass

                    likes_elem = comment.select_one("span.likes")
                    likes = self._parse_count(likes_elem.get_text(strip=True) if likes_elem else "0")

                    reply_elem = comment.select_one("span.reply-count")
                    comments = self._parse_count(reply_elem.get_text(strip=True) if reply_elem else "0")

                    result = self._create_standard_item(
                        platform=self.platform,
                        author=author,
                        content=content,
                        time=post_time,
                        likes=likes,
                        comments=comments,
                        tags=[keyword, "京东", f"评分{rating}星"]
                    )
                    results.append(result)

                except Exception as e:
                    self.logger.debug(f"Error parsing comment: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing comments page: {str(e)}")

        return results

    def _parse_count(self, count_str: str) -> int:
        if not count_str:
            return 0
        count_str = count_str.strip()
        if '万' in count_str:
            return int(float(count_str.replace('万', '')) * 10000)
        try:
            return int(count_str)
        except ValueError:
            return 0


class TaobaoCommentScraper(BaseScraper):
    PLATFORM_NAME = "淘宝"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.session = requests.Session()
        self.headers = self._get_headers()
        self.headers["Referer"] = "https://www.taobao.com"

    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                self._random_delay(2, 5)
                response = self.session.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    self.logger.warning("Taobao access forbidden")
            except requests.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
        return None

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        page = 1

        search_url = f"https://s.taobao.com/search?q={keyword}"
        html = self._make_request(search_url)

        if not html:
            return self._fallback_to_mock(keyword, max_count)

        product_ids = self._extract_product_ids(html)

        for idx, pid in enumerate(product_ids[:10]):
            if len(results) >= max_count:
                break

            comments_url = f"https://detail.tmall.com/item.htm?id={pid}"
            comments_html = self._make_request(comments_url)

            if comments_html:
                items = self._parse_comments(comments_html, keyword)
                results.extend(items)

            self._random_delay(3, 7)

        if not results:
            return self._fallback_to_mock(keyword, max_count)

        return results[:max_count]

    def _extract_product_ids(self, html: str) -> List[str]:
        ids = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select("div[data-item-id]") or soup.select("div.item"):
                pid = item.get("data-item-id") or re.search(r'id=(\d+)', str(item))
                if pid:
                    ids.append(str(pid))
        except Exception as e:
            self.logger.debug(f"Error extracting product IDs: {str(e)}")
        return ids[:20]

    def _parse_comments(self, html: str, keyword: str) -> List[Dict]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            for comment in soup.select("div.review-item") or soup.select("div.tb-reviews-item"):
                try:
                    content_elem = comment.select_one("div.review-content") or comment.select_one("p.r-content")
                    content = content_elem.get_text(strip=True) if content_elem else ""

                    if len(content) < 5:
                        continue

                    author_elem = comment.select_one("div.user-name") or comment.select_one("span.user-nickname")
                    author = author_elem.get_text(strip=True) if author_elem else "淘宝买家"

                    time_elem = comment.select_one("div.review-date") or comment.select_one("span.date")
                    post_time = time_elem.get_text(strip=True) if time_elem else ""

                    star_elem = comment.select_one("div.star") or comment.select_one("i.tb-icon-stars")
                    rating = 5
                    if star_elem:
                        star_class = star_elem.get("class", [])
                        for cls in star_class:
                            if 'star' in cls.lower() and re.search(r'\d', cls):
                                rating = int(re.search(r'\d', cls).group())

                    likes_elem = comment.select_one("span.useful-count")
                    likes = self._parse_count(likes_elem.get_text(strip=True) if likes_elem else "0")

                    result = self._create_standard_item(
                        platform=self.platform,
                        author=author,
                        content=content,
                        time=post_time,
                        likes=likes,
                        comments=0,
                        tags=[keyword, "淘宝", f"评分{rating}星"]
                    )
                    results.append(result)

                except Exception as e:
                    self.logger.debug(f"Error parsing comment: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing comments page: {str(e)}")

        return results

    def _parse_count(self, count_str: str) -> int:
        if not count_str:
            return 0
        count_str = count_str.strip()
        if '万' in count_str:
            return int(float(count_str.replace('万', '')) * 10000)
        try:
            return int(count_str)
        except ValueError:
            return 0


class EcommerceCommentScraper(BaseScraper):
    PLATFORM_NAME = "电商评论"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.jd_scraper = JDCommentScraper()
        self.taobao_scraper = TaobaoCommentScraper()

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        half = max_count // 2

        self.logger.info(f"Scraping JD comments for: {keyword}")
        try:
            results.extend(self.jd_scraper.scrape(keyword, half))
        except Exception as e:
            self.logger.error(f"JD scraper failed: {str(e)}")

        self._random_delay(3, 6)

        self.logger.info(f"Scraping Taobao comments for: {keyword}")
        try:
            results.extend(self.taobao_scraper.scrape(keyword, half))
        except Exception as e:
            self.logger.error(f"Taobao scraper failed: {str(e)}")

        return results[:max_count]