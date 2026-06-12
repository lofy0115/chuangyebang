"""
国际平台数据源（翻墙后可访问）
支持: Twitter/X, Reddit, Amazon, Trustpilot
"""
from typing import List, Dict, Optional
import requests
import logging
import random
from datetime import datetime

from .base_datasource import BaseDataSource, PlatformType, NormalizedComplaint


class TwitterDataSource(BaseDataSource):
    """
    Twitter/X API v2 数据源

    获取 API Key:
    1. https://developer.twitter.com/en/portal/dashboard 创建项目
    2. 获取 Bearer Token
    3. 填入 config 或环境变量 TWITTER_BEARER_TOKEN

    免费 tier: 500k tweets/month, 15 tweets/15min search
    """
    name = "twitter"
    platform_type = PlatformType.INTERNATIONAL
    description = "Twitter/X API v2，支持搜索推文"
    docs_url = "https://developer.twitter.com/en/docs/twitter-api"

    API_BASE = "https://api.twitter.com/2"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.bearer_token = self.config.get("bearer_token") or self.config.get("TWITTER_BEARER_TOKEN", "")
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return bool(self.bearer_token)

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """
        搜索推文
        GET /2/tweets/search/recent
        免费版只支持最近7天的搜索
        """
        if not self.is_configured:
            self.logger.warning("Twitter API 未配置 Bearer Token，使用 mock")
            return self._mock_tweets(keyword, max_count)

        # Twitter API 参数
        params = {
            "query": f"{keyword} lang:zh -is:retweet",  # 中文关键词，排除转发
            "max_results": min(max_count, 100),
            "tweet.fields": "created_at,public_metrics,author_id,id",
            "expansions": "author_id",
            "user.fields": "name,username",
        }

        headers = {"Authorization": f"Bearer {self.bearer_token}"}

        try:
            resp = requests.get(
                f"{self.API_BASE}/tweets/search/recent",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            data = resp.json()
        except requests.exceptions.Timeout:
            self.logger.warning("Twitter API 超时")
            return self._mock_tweets(keyword, max_count)
        except Exception as e:
            self.logger.warning(f"Twitter API 错误: {e}")
            return self._mock_tweets(keyword, max_count)

        if resp.status_code != 200:
            self.logger.warning(f"Twitter API HTTP {resp.status_code}: {data}")
            return self._mock_tweets(keyword, max_count)

        # 构建用户映射
        users = {}
        for u in data.get("includes", {}).get("users", []):
            users[u["id"]] = u

        results = []
        for t in data.get("data", []):
            author = users.get(t.get("author_id", ""), {})
            metrics = t.get("public_metrics", {})

            results.append(NormalizedComplaint(
                content=t.get("text", ""),
                platform="Twitter",
                author=author.get("username", author.get("name", "unknown")),
                likes=metrics.get("like_count", 0),
                comments=metrics.get("reply_count", 0),
                shares=metrics.get("retweet_count", 0),
                published_at=t.get("created_at", "")[:10] if t.get("created_at") else "",
                url=f"https://twitter.com/i/web/status/{t['id']}",
                tags=[keyword],
                sentiment=self._guess_sentiment(t.get("text", "")),
                source_type="social"
            ))

        if not results:
            return self._mock_tweets(keyword, max_count)
        return results[:max_count]

    def _guess_sentiment(self, text: str) -> str:
        neg = sum(w in text.lower() for w in ["bad", "terrible", "awful", "scam", "fake", "worst", "hate", "angry", "disappointed", "problem", "broken"])
        pos = sum(w in text.lower() for w in ["good", "great", "awesome", "excellent", "love", "best", "amazing", "perfect", "recommend", "happy"])
        if neg > pos:
            return "negative"
        elif pos > neg:
            return "positive"
        return "neutral"

    def _mock_tweets(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Has anyone had issues with {keyword}? The quality seems inconsistent.", "author": "techreviewer", "likes": random.randint(10, 200), "comments": random.randint(5, 50)},
            {"content": f"After testing {keyword} for a month, here's my honest review... #honest", "author": "reviewer_jane", "likes": random.randint(50, 500), "comments": random.randint(10, 100)},
            {"content": f"Beware of hidden fees with {keyword}. They advertise one price but charge more at checkout.", "author": "consumer_adv", "likes": random.randint(100, 1000), "comments": random.randint(20, 200)},
        ]
        return [self._normalize(item, "Twitter") for item in mock[:max_count]]


class RedditDataSource(BaseDataSource):
    """
    Reddit API (无认证可用，Public Rate Limit: 60 requests/minute)

    Reddit 的 JSON API:
    - 搜索: https://www.reddit.com/search.json?q=keyword
    - 子版块热帖: https://www.reddit.com/r/{subreddit}/hot.json
    """
    name = "reddit"
    platform_type = PlatformType.INTERNATIONAL
    description = "Reddit 搜索和热帖，无需 API Key"
    docs_url = "https://www.reddit.com/dev/api"

    REDDIT_BASE = "https://www.reddit.com"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return True  # 无需认证始终可用（有频率限制）

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """搜索 Reddit 帖子"""
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ChuangYeBang/1.0; +https://github.com/lofy0115)",
            "Accept": "application/json",
        }

        params = {
            "q": keyword,
            "sort": "relevance",
            "t": "all",        # all time
            "limit": min(max_count, 25),
        }

        try:
            resp = requests.get(
                f"{self.REDDIT_BASE}/search.json",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            data = resp.json()
        except Exception as e:
            self.logger.warning(f"Reddit 搜索失败: {e}")
            return self._mock_reddit(keyword, max_count)

        results = []
        children = data.get("data", {}).get("children", [])
        for child in children:
            post = child.get("data", {})
            if post.get("is_self"):  # 只取文字帖
                results.append(NormalizedComplaint(
                    content=post.get("selftext", post.get("title", ""))[:500],
                    platform="Reddit",
                    author=post.get("author", "unknown"),
                    likes=post.get("ups", 0),
                    comments=post.get("num_comments", 0),
                    published_at=datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d") if post.get("created_utc") else "",
                    url=f"https://reddit.com{post.get('permalink', '')}",
                    tags=[keyword, post.get("subreddit", "")],
                    sentiment=self._guess_sentiment(post.get("title", "") + " " + post.get("selftext", "")),
                    source_type="social"
                ))

        if not results:
            return self._mock_reddit(keyword, max_count)
        return results[:max_count]

    def _guess_sentiment(self, text: str) -> str:
        text_lower = text.lower()
        neg = sum(w in text_lower for w in ["bad", "terrible", "awful", "scam", "fake", "worst", "hate", "disappointed", "problem", "broken", "sucks"])
        pos = sum(w in text_lower for w in ["good", "great", "awesome", "excellent", "love", "best", "amazing", "perfect", "recommend"])
        if neg > pos:
            return "negative"
        elif pos > neg:
            return "positive"
        return "neutral"

    def _mock_reddit(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Warning: {keyword} has serious quality control issues. Here's my experience after 3 months of use...", "author": "Throwaway_user123", "likes": random.randint(100, 2000), "comments": random.randint(20, 300)},
            {"content": f"Has anyone else noticed that {keyword} prices keep going up while quality goes down? Discussion thread.", "author": "concerned_customer", "likes": random.randint(50, 800), "comments": random.randint(10, 150)},
        ]
        return [self._normalize(item, "Reddit") for item in mock[:max_count]]


class AmazonReviewsDataSource(BaseDataSource):
    """
    亚马逊商品评论数据源

    使用 Amazon Product Advertising API 或直接爬取（翻墙后可用）
    简单方案: 直接请求亚马逊搜索页 HTML（反爬严格，建议用 RapidAPI）
    """
    name = "amazon"
    platform_type = PlatformType.ECOMMERCE_INT
    description = "亚马逊商品评论（需翻墙）"
    docs_url = "https://developer-docs.amazon.com/product-advertising-api"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.access_key = self.config.get("access_key") or self.config.get("AWS_ACCESS_KEY", "")
        self.secret_key = self.config.get("secret_key") or self.config.get("AWS_SECRET_KEY", "")
        self.associate_tag = self.config.get("associate_tag") or self.config.get("AWS_ASSOCIATE_TAG", "")
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return bool(self.access_key and self.secret_key)  # 需要 PA-API 凭证

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """
        搜索亚马逊商品评论
        免费方案：使用 RapidAPI Amazon Reviews API
        """
        rapidapi_key = self.config.get("rapidapi_key") or self.config.get("RAPIDAPI_KEY", "")

        if rapidapi_key:
            return self._search_via_rapidapi(keyword, max_count, rapidapi_key)

        if not self.is_configured:
            self.logger.warning("Amazon API 未配置，使用 mock")
            return self._mock_amazon(keyword, max_count)

        # TODO: 实现 PA-API 调用
        return self._mock_amazon(keyword, max_count)

    def _search_via_rapidapi(self, keyword: str, max_count: int, api_key: str) -> List[NormalizedComplaint]:
        """通过 RapidAPI Amazon Reviews API 搜索"""
        try:
            resp = requests.get(
                "https://amazon23.p.rapidapi.com/product/reviews",
                params={"asin": keyword, "country": "us", "page": "1"},
                headers={
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "amazon23.p.rapidapi.com"
                },
                timeout=self.timeout
            )
            data = resp.json()
            results = []
            for item in data.get("result", [])[:max_count]:
                results.append(NormalizedComplaint(
                    content=item.get("review", item.get("title", "")),
                    platform="Amazon",
                    author=item.get("reviewer", item.get("name", "Anonymous")),
                    likes=item.get("helpful_votes", 0),
                    comments=0,
                    published_at=item.get("date", ""),
                    rating=item.get("rating", 0),
                    tags=[keyword, "Amazon"],
                    sentiment=self._sentiment_from_rating(item.get("rating", 3)),
                    source_type="ecommerce"
                ))
            return results
        except Exception as e:
            self.logger.warning(f"RapidAPI Amazon 失败: {e}")
            return self._mock_amazon(keyword, max_count)

    def _sentiment_from_rating(self, rating: float) -> str:
        if rating >= 4:
            return "positive"
        elif rating <= 2:
            return "negative"
        return "neutral"

    def _mock_amazon(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Verified Purchase - {keyword} quality is not as described. Received damaged item.", "author": "John D.", "likes": random.randint(5, 50), "rating": 1.0, "date": "2025-03-15"},
            {"content": f"Decent product for the price but there are better alternatives available.", "author": "Sarah M.", "likes": random.randint(3, 30), "rating": 3.0, "date": "2025-03-10"},
            {"content": f"Excellent value! Exactly what I needed and shipping was fast.", "author": "Mike R.", "likes": random.randint(10, 100), "rating": 5.0, "date": "2025-03-08"},
        ]
        return [self._normalize(item, "Amazon") for item in mock[:max_count]]


class TrustpilotDataSource(BaseDataSource):
    """
    Trustpilot 评价数据源（国际权威点评平台）

    API: https://developers.trustpilot.com/
    免费 API: 160 requests/hour (需要 API Key)
    """
    name = "trustpilot"
    platform_type = PlatformType.INTERNATIONAL
    description = "Trustpilot 国际企业评价"
    docs_url = "https://developers.trustpilot.com/"

    API_BASE = "https://api.trustpilot.com/v1"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key") or self.config.get("TRUSTPILOT_API_KEY", "")
        self.business_unit_id = self.config.get("business_unit_id") or self.config.get("TRUSTPILOT_BUSINESS_UNIT", "")
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.business_unit_id)

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """搜索 Trustpilot 企业评价"""
        if not self.is_configured:
            return self._mock_trustpilot(keyword, max_count)

        headers = {"apikey": self.api_key}
        params = {"apikey": self.api_key, "limit": min(max_count, 20)}

        try:
            resp = requests.get(
                f"{self.API_BASE}/business-units/{self.business_unit_id}/reviews",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            data = resp.json()
        except Exception as e:
            self.logger.warning(f"Trustpilot API 失败: {e}")
            return self._mock_trustpilot(keyword, max_count)

        results = []
        for review in data.get("reviews", []):
            stars = review.get("stars", 3)
            results.append(NormalizedComplaint(
                content=review.get("text", ""),
                platform="Trustpilot",
                author=review.get("consumer", {}).get("displayName", "Anonymous"),
                likes=review.get("helpful", 0),
                comments=0,
                published_at=review.get("createdAt", "")[:10] if review.get("createdAt") else "",
                rating=stars,
                tags=[keyword, "Trustpilot"],
                sentiment=self._sentiment_from_rating(stars),
                source_type="social"
            ))

        if not results:
            return self._mock_trustpilot(keyword, max_count)
        return results[:max_count]

    def _sentiment_from_rating(self, stars: int) -> str:
        if stars >= 4:
            return "positive"
        elif stars <= 2:
            return "negative"
        return "neutral"

    def _mock_trustpilot(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Outstanding service from {keyword}. Highly recommend to anyone looking for quality.", "author": "James W.", "rating": 5, "date": "2025-03-01"},
            {"content": f"Average experience. Nothing special but got the job done.", "author": "Emily R.", "rating": 3, "date": "2025-02-28"},
            {"content": f"Terrible experience. Customer support is non-existent and product broke after 1 week.", "author": "David K.", "rating": 1, "date": "2025-02-25"},
        ]
        return [self._normalize(item, "Trustpilot") for item in mock[:max_count]]