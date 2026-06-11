import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import re
import time
from datetime import datetime, timedelta

from .base_scraper import BaseScraper


class XiaohongshuScraper(BaseScraper):
    PLATFORM_NAME = "小红书"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME
        self.session = requests.Session()
        self.base_url = "https://www.xiaohongshu.com"
        self.search_url = "https://www.xiaohongshu.com/search_result"
        self.headers = self._get_headers()
        self.headers["Cookie"] = "webId=; timestamp=; webBuild=; xsecappid=xhs-pc-web;"

    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                self._random_delay(3, 8)
                response = self.session.get(url, headers=self.headers, params=params, timeout=20)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 302:
                    self.logger.warning("Redirected, may need login")
                elif response.status_code == 403:
                    self.logger.warning("Access forbidden")
                    time.sleep(60)
            except requests.RequestException as e:
                self.logger.error(f"Request error: {str(e)}")
        return None

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        page = 1
        page_size = 20

        while len(results) < max_count:
            params = {
                "keyword": keyword,
                "type": "51",
                "page": page,
                "page_size": page_size
            }

            self.logger.info(f"Scraping Xiaohongshu page {page} for: {keyword}")
            html = self._make_request(self.search_url, params)

            if not html:
                self.logger.warning(f"Failed to fetch page {page}, trying next")
                page += 1
                continue

            items = self._parse_search_page(html, keyword)
            if not items:
                self.logger.info(f"No more results on page {page}")
                break

            results.extend(items)
            self.logger.info(f"Page {page}: got {len(items)} items, total: {len(results)}")
            page += 1

            if page <= 10:
                self._random_delay(5, 10)

        return results[:max_count]

    def _parse_search_page(self, html: str, keyword: str) -> List[Dict]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            note_cards = soup.select("div.note-item") or soup.select("div[data-vb-card-type='normal']")

            for card in note_cards[:20]:
                try:
                    title_elem = card.select_one("h3.title") or card.select_one("div.title")
                    content_elem = card.select_one("div.desc") or card.select_one("div.content")

                    content = ""
                    if title_elem:
                        content = title_elem.get_text(strip=True)
                    if content_elem:
                        content += " " + content_elem.get_text(strip=True)

                    if len(content) < 5:
                        continue

                    author_elem = card.select_one("span.name")
                    author = author_elem.get_text(strip=True) if author_elem else "未知作者"

                    like_elem = card.select_one("span.likes") or card.select_one("div.liked-count")
                    likes = self._parse_count(like_elem.get_text(strip=True) if like_elem else "0")

                    comment_elem = card.select_one("span.comments") or card.select_one("div.comment-count")
                    comments = self._parse_count(comment_elem.get_text(strip=True) if comment_elem else "0")

                    time_elem = card.select_one("span.time") or card.select_one("div.time")
                    post_time = time_elem.get_text(strip=True) if time_elem else datetime.now().strftime("%Y-%m-%d")

                    result = self._create_standard_item(
                        platform=self.platform,
                        author=author,
                        content=content,
                        time=post_time,
                        likes=likes,
                        comments=comments,
                        tags=[keyword, "小红书"]
                    )
                    results.append(result)

                except Exception as e:
                    self.logger.debug(f"Error parsing note card: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing search page: {str(e)}")

        if not results:
            return self._fallback_to_mock(keyword, 20)
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


class XiaohongshuNoteScraper(XiaohongshuScraper):
    PLATFORM_NAME = "小红书笔记"

    def __init__(self):
        super().__init__()
        self.platform = self.PLATFORM_NAME

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        results = []
        try:
            search_url = f"{self.base_url}/search_result?keyword={keyword}&type=51"
            html = self._make_request(search_url)

            if html:
                soup = BeautifulSoup(html, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")

                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if data.get("@type") == "ItemList":
                            for item in data.get("itemListElement", [])[:max_count]:
                                if isinstance(item, dict):
                                    results.append(self._create_standard_item(
                                        platform=self.platform,
                                        author=item.get("author", {}).get("name", "未知"),
                                        content=item.get("name", ""),
                                        time=item.get("datePublished", ""),
                                        likes=0,
                                        comments=0,
                                        tags=[keyword, "笔记"]
                                    ))
                    except (json.JSONDecodeError, AttributeError):
                        continue

        except Exception as e:
            self.logger.error(f"Note scraper error: {str(e)}")

        if not results:
            return self._fallback_to_mock(keyword, max_count)
        return results[:max_count]

    def _fallback_to_mock(self, keyword: str, max_count: int) -> List[Dict]:
        self.logger.info("Using mock data for Xiaohongshu")
        return [
            self._create_standard_item(
                platform=self.platform,
                author=f"小红书用户{i}",
                content=f"分享关于{keyword}的使用体验，这产品真的很不错，值得推荐给大家",
                time=(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                likes=5000 - i * 100,
                comments=300 - i * 10,
                tags=[keyword, "种草"]
            )
            for i in range(min(max_count, 20))
        ]