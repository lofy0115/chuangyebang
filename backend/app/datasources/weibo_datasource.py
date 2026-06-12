"""
微博开放平台数据源
文档: https://open.weibo.com/wiki/API
需要 access_token 才能调用大多数 API

获取 access_token:
1. 在 https://open.weibo.com 创建 App（选择"移动应用"或"网站"）
2. 获取 App Key
3. OAuth2 授权获取 access_token
4. 将 access_token 填入 config 或环境变量 WEIBO_ACCESS_TOKEN
"""
from typing import List, Dict, Optional
import requests
import logging
import json
from datetime import datetime

from .base_datasource import BaseDataSource, PlatformType, NormalizedComplaint


class WeiboDataSource(BaseDataSource):
    """微博开放平台 API"""

    name = "weibo"
    platform_type = PlatformType.DOMESTIC_CN
    description = "微博开放平台 API，支持搜索和热搜榜"
    docs_url = "https://open.weibo.com/wiki/API"

    # 微博 API 端点
    API_BASE = "https://api.weibo.com/2"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.app_key = self.config.get("app_key") or self.config.get("WEIBO_APP_KEY", "")
        self.access_token = self.config.get("access_token") or self.config.get("WEIBO_ACCESS_TOKEN", "")
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        """是否已配置（需要 access_token）"""
        return bool(self.access_token and self.app_key)

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """
        搜索微博内容
        API: GET https://api.weibo.com/2/search/statuses.json
        """
        if not self.is_configured:
            self.logger.warning("微博未配置 access_token，使用 mock 数据")
            return self._mock_search(keyword, max_count)

        results = []
        page_size = min(max_count, 50)
        pages = (max_count + page_size - 1) // page_size

        for page in range(1, pages + 1):
            if len(results) >= max_count:
                break

            params = {
                "access_token": self.access_token,
                "q": keyword,
                "count": page_size,
                "page": page,
                "base_app": 0,          # 0=全站, 1=仅本应用
                "filter_type": 0,
            }

            try:
                resp = requests.get(
                    f"{self.API_BASE}/search/statuses.json",
                    params=params,
                    timeout=self.timeout
                )
                data = resp.json()
            except requests.exceptions.Timeout:
                self.logger.warning(f"微博搜索超时: {keyword} page={page}")
                break
            except Exception as e:
                self.logger.warning(f"微博搜索失败: {e}")
                break

            if data.get("error"):
                self.logger.warning(f"微博 API 错误: {data.get('error')}")
                break

            statuses = data.get("statuses", [])
            if not statuses:
                break

            for s in statuses:
                results.append(self._parse_status(s))

        if not results:
            self.logger.info("微博 API 无结果，使用 mock")
            return self._mock_search(keyword, max_count)

        return results[:max_count]

    def _parse_status(self, s: Dict) -> NormalizedComplaint:
        """解析微博状态为标准格式"""
        # 解析时间
        created_at = s.get("created_at", "")
        try:
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = created_at[:10] if len(created_at) >= 10 else ""

        # 处理转发
        text = s.get("text", "")
        retweeted = s.get("retweeted_status")
        if retweeted:
            text = f"转发: {retweeted.get('text', '')}"

        # 用户信息
        user = s.get("user", {})
        author = user.get("screen_name", "微博用户")

        return NormalizedComplaint(
            content=self._clean_html(text),
            platform="微博",
            author=author,
            likes=s.get("attitudes_count", 0),
            comments=s.get("comments_count", 0),
            shares=s.get("reposts_count", 0),
            published_at=date_str,
            url=f"https://weibo.com/{user.get('id','')}/{s.get('id','')}",
            tags=self._extract_tags(s.get("topics", [])),
            sentiment=self._guess_sentiment(text),
            source_type="social"
        )

    def _clean_html(self, text: str) -> str:
        """清理 HTML 标签"""
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        return text.strip()

    def _extract_tags(self, topics: List) -> List[str]:
        """提取话题标签"""
        return [t.get("topic", t.get("name", "")) for t in topics if t] if topics else []

    def _guess_sentiment(self, text: str) -> str:
        """简单情感判断"""
        neg = sum(w in text for w in ["差", "烂", "坑", "骗", "垃圾", "垃圾", "糟糕", "失望", "后悔", "投诉", "问题", "故障", "虚标", "太贵"])
        pos = sum(w in text for w in ["好", "棒", "赞", "推荐", "满意", "喜欢", "优秀", "给力"])
        if neg > pos:
            return "negative"
        elif pos > neg:
            return "positive"
        return "neutral"

    def _mock_search(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        """Mock 数据"""
        import random
        mock_items = [
            {"content": f"关于{keyword}的微博讨论：质量参差不齐，消费者需谨慎选择", "author": "微博用户A", "likes": random.randint(50, 300), "comments": random.randint(10, 80)},
            {"content": f"{keyword}行业观察：服务体验差距大，头部品牌优势明显", "author": "行业分析员", "likes": random.randint(100, 500), "comments": random.randint(20, 100)},
            {"content": f"真实吐槽{keyword}：交钱之前态度好，交钱之后无人理", "author": "消费者维权", "likes": random.randint(80, 400), "comments": random.randint(15, 60)},
            {"content": f"深度测评{keyword}：性价比分析报告（附建议）", "author": "测评达人", "likes": random.randint(200, 800), "comments": random.randint(30, 120)},
            {"content": f"{keyword}避坑指南，这些问题一定要看", "author": "生活博主", "likes": random.randint(150, 600), "comments": random.randint(25, 90)},
        ]
        selected = random.sample(mock_items, min(max_count, len(mock_items)))
        return [self._normalize(item, "微博") for item in selected]


class WeiboHotSearchDataSource(BaseDataSource):
    """微博热搜榜数据源"""

    name = "weibo_hot"
    platform_type = PlatformType.DOMESTIC_CN
    description = "微博实时热搜榜"
    docs_url = "https://open.weibo.com/wiki/Suggestions/hot_trends"

    API_BASE = "https://api.weibo.com/2"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.app_key = self.config.get("app_key") or self.config.get("WEIBO_APP_KEY", "")
        self.access_token = self.config.get("access_token") or self.config.get("WEIBO_ACCESS_TOKEN", "")
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token and self.app_key)

    def search(self, keyword: str = "", max_count: int = 50) -> List[NormalizedComplaint]:
        """
        获取微博热搜榜，可按关键词筛选
        API: GET https://api.weibo.com/2/suggestions/hot_trends.json
        """
        if not self.is_configured:
            self.logger.warning("微博热搜未配置 access_token，使用 mock")
            return self._mock_hot(keyword, max_count)

        params = {
            "access_token": self.access_token,
            "app_key": self.app_key,
        }

        try:
            resp = requests.get(
                f"{self.API_BASE}/suggestions/hot_trends.json",
                params=params,
                timeout=self.timeout
            )
            data = resp.json()
        except Exception as e:
            self.logger.warning(f"微博热搜获取失败: {e}")
            return self._mock_hot(keyword, max_count)

        if data.get("error"):
            self.logger.warning(f"微博热搜 API 错误: {data.get('error')}")
            return self._mock_hot(keyword, max_count)

        trends = data.get("trends", [])
        results = []
        for t in trends:
            name = t.get("name", "")
            if keyword and keyword not in name:
                continue
            results.append(NormalizedComplaint(
                content=f"【热搜】{name}：{t.get('query', name)}",
                platform="微博热搜",
                author=None,
                likes=t.get("num", 0),
                comments=0,
                published_at=datetime.now().strftime("%Y-%m-%d"),
                url=t.get("url", ""),
                tags=["热搜", name.strip("#")],
                sentiment="neutral",
                source_type="search"
            ))

        return results[:max_count]

    def _mock_hot(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock_trends = [
            "民宿预订陷阱曝光",
            "新能源汽车续航实测",
            "奶茶糖分超标",
            "消费者维权成功案例",
            "电商平台服务评价",
            "国货品牌崛起",
            "直播带货投诉激增",
            "预付卡消费套路",
            "网红餐厅实地测评",
            "数码产品避坑指南",
        ]
        filtered = [t for t in mock_trends if not keyword or keyword in t]
        return [
            NormalizedComplaint(
                content=f"【热搜】{t}",
                platform="微博热搜",
                author=None,
                likes=random.randint(10000, 500000),
                comments=random.randint(100, 5000),
                published_at=datetime.now().strftime("%Y-%m-%d"),
                tags=["热搜"],
                sentiment="neutral",
                source_type="search"
            )
            for t in filtered[:max_count]
        ]


class ZhihuDataSource(BaseDataSource):
    """知乎数据源（搜索 + 热榜）"""

    name = "zhihu"
    platform_type = PlatformType.DOMESTIC_CN
    description = "知乎搜索和热榜"
    docs_url = "https://www.zhihu.com/api/v4"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.access_token = self.config.get("access_token") or self.config.get("ZHIHU_ACCESS_TOKEN", "")
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        # 知乎部分 API 无需登录，但有频率限制
        return True  # 始终可用（有限流）

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """搜索知乎问答"""
        import random
        # 知乎搜索 API
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        params = {
            "q": keyword,
            "limit": min(max_count, 20),
            "offset": 0,
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            resp = requests.get(
                "https://www.zhihu.com/api/v4/search_v3",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}")
            data = resp.json()
        except Exception as e:
            self.logger.warning(f"知乎搜索失败: {e}")
            return self._mock_zhihu(keyword, max_count)

        results = []
        for item in data.get("data", []):
            obj = item.get("object", {})
            if obj.get("type") not in ("answer", "article", "question"):
                continue
            question = obj.get("question", {})
            title = question.get("title", obj.get("title", ""))
            excerpt = obj.get("excerpt", "")

            results.append(NormalizedComplaint(
                content=f"{title} {excerpt}".strip(),
                platform="知乎",
                author=obj.get("author", {}).get("name"),
                likes=obj.get("voteup_count", 0),
                comments=obj.get("comment_count", 0),
                published_at=None,
                tags=[keyword, "知乎"],
                sentiment="neutral",
                source_type="social"
            ))

        if not results:
            return self._mock_zhihu(keyword, max_count)
        return results[:max_count]

    def _mock_zhihu(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock_items = [
            {"content": f"关于{keyword}的深度分析：从用户痛点看行业机会", "author": "创业者老王", "likes": random.randint(200, 1000), "comments": random.randint(20, 80)},
            {"content": f"{keyword}有哪些坑？过来人经验分享", "author": "匿名用户", "likes": random.randint(100, 500), "comments": random.randint(10, 50)},
        ]
        return [self._normalize(item, "知乎") for item in mock_items[:max_count]]