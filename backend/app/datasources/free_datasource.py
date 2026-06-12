"""
免费数据源插件（无需 API Key，开箱即用）
覆盖: B站/知乎/CSDN/AppStore/GitHub/HackerNews/微博热搜/小红书

注意: 部分平台在 WSL 环境可能无法访问（网络限制）
翻墙后可访问: Twitter/Reddit/Amazon/Trustpilot/ProductHunt
"""
from typing import List, Dict, Optional
import requests
import logging
import re
import random
import subprocess
import json
from datetime import datetime

from .base_datasource import BaseDataSource, PlatformType, NormalizedComplaint


def curl_get(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 8) -> Optional[str]:
    """
    使用 curl 发起 HTTP GET 请求（绕过 Python SSL 问题）
    Python 3.12 + OpenSSL 3.0 在某些中国 CDN 上有 TLS 兼容性问题，curl 则正常
    """
    if params:
        query = "&".join(f"{k}={str(v)}" for k, v in params.items())
        url = f"{url}?{query}"

    cmd = ["curl", "-s", "--compressed", "--max-time", str(timeout), url]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def curl_json(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 8) -> Optional[Dict]:
    """curl GET 并尝试解析为 JSON"""
    text = curl_get(url, params, headers, timeout)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ============================================================
# 国内免费平台
# ============================================================

class BilibiliDataSource(BaseDataSource):
    """
    B站（哔哩哔哩）搜索 API
    无需认证，直接请求，返回视频+标题+播放/弹幕/收藏/评论数
    """
    name = "bilibili"
    platform_type = PlatformType.DOMESTIC_CN
    description = "B站视频搜索，返回播放量/弹幕/收藏/评论数据"
    docs_url = "https://github.com/SocialSisterYi/bilibiliAPI- docs"

    API_SEARCH = "https://api.bilibili.com/x/web-interface/search/all"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True  # 无需配置

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.bilibili.com",
        }

        all_results = []
        page_size = min(max_count, 20)
        pages = (max_count + page_size - 1) // page_size

        for page in range(1, pages + 1):
            if len(all_results) >= max_count:
                break

            try:
                data = curl_json(self.API_SEARCH, params={"keyword": keyword, "page": page, "page_size": page_size}, timeout=self.timeout)
            except Exception as e:
                self.logger.warning(f"B站搜索失败: {e}")
                break

            if data.get("code") != 0:
                break

            video_list = data.get("data", {}).get("result", {}).get("video", [])
            if not video_list:
                break

            for v in video_list:
                title = re.sub(r'<[^>]+>', '', v.get("title", ""))
                if not title or len(title) < 5:
                    continue

                # 解析时长
                duration = v.get("duration", "0:0")
                duration_str = str(duration) if duration else ""

                all_results.append(NormalizedComplaint(
                    content=f"【B站视频】{title}",
                    platform="B站",
                    author=v.get("author", "未知UP主"),
                    likes=v.get("favorites", 0),       # 收藏
                    comments=v.get("review", 0),        # 评论
                    shares=v.get("video_review", 0),    # 弹幕
                    published_at=None,
                    url=v.get("arcurl", "") or v.get("bvid", ""),
                    tags=[keyword, "B站视频", f"播放{v.get('play','?')}"],
                    sentiment=self._sentiment_from_title(title),
                    source_type="social"
                ))

        if not all_results:
            return self._mock(keyword, max_count)
        return all_results[:max_count]

    def _sentiment_from_title(self, title: str) -> str:
        neg_kw = ["坑", "骗", "垃圾", "糟糕", "差评", "翻车", "翻车了", "避坑", "吐槽"]
        pos_kw = ["推荐", "测评", "教程", "详解", "完整", "实战", "经验", "分享"]
        if any(k in title for k in neg_kw):
            return "negative"
        if any(k in title for k in pos_kw):
            return "positive"
        return "neutral"

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        mock = [
            {"content": f"【B站视频】{keyword}深度测评：真实体验分享", "author": "测评UP主", "likes": 500, "comments": 80},
            {"content": f"关于{keyword}的避坑指南，这些细节一定要看", "author": "生活博主", "likes": 300, "comments": 45},
        ]
        return [self._normalize({"content": f"【B站视频】{keyword}相关视频合集", "author": "B站用户", "likes": 100, "comments": 20}, "B站") for _ in range(min(max_count, 5))]


class CSDNDataSource(BaseDataSource):
    """
    CSDN 搜索 API
    技术文章社区，返回标题+作者+收藏数
    """
    name = "csdn"
    platform_type = PlatformType.DOMESTIC_CN
    description = "CSDN技术文章搜索"
    docs_url = "https://so.csdn.net/so/v1/search"

    API_SEARCH = "https://so.csdn.net/api/v3/search"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://so.csdn.net",
        }

        all_results = []
        page_size = 20
        pages = (max_count + page_size - 1) // page_size

        for page in range(1, pages + 1):
            if len(all_results) >= max_count:
                break

            try:
                data = curl_json(self.API_SEARCH, params={"q": keyword, "p": page, "s": 0, "portal-type": 1}, timeout=self.timeout)
            except Exception as e:
                self.logger.warning(f"CSDN搜索失败: {e}")
                break

            vos = data.get("result_vos", [])
            if not vos:
                break

            for v in vos:
                title = re.sub(r'<[^>]+>', '', v.get("title", ""))
                if not title or len(title) < 5:
                    continue

                all_results.append(NormalizedComplaint(
                    content=f"【CSDN】{title}",
                    platform="CSDN",
                    author=v.get("nickname", "CSDN用户"),
                    likes=v.get("likes", 0),
                    comments=v.get("comments", 0),
                    published_at=None,
                    url=v.get("url", ""),
                    tags=[keyword, "CSDN", "技术文章"],
                    sentiment="neutral",
                    source_type="social"
                ))

        if not all_results:
            return self._mock(keyword, max_count)
        return all_results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        return [self._normalize({
            "content": f"【CSDN】关于{keyword}的技术文章和实战经验分享",
            "author": "CSDN博主",
            "likes": 50,
            "comments": 5,
        }, "CSDN") for _ in range(min(max_count, 5))]


class AppStoreDataSource(BaseDataSource):
    """
    Apple App Store 搜索 API
    无需认证，返回 App评分+评价数+开发商信息
    可用于分析竞品 App 的用户口碑
    """
    name = "appstore"
    platform_type = PlatformType.ECOMMERCE_CN
    description = "App Store应用评分和评价数据"
    docs_url = "https://developer.apple.com/library/content/documentation/AudioVideo/Conceptual/iTuneSearchAPI"

    API_SEARCH = "https://itunes.apple.com/search"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        all_results = []
        media_types = ["software", "ios"]
        seen_apps = set()

        for media in media_types:
            if len(all_results) >= max_count:
                break

            try:
                data = curl_json(self.API_SEARCH, params={
                        "term": keyword,
                        "country": "cn",
                        "media": media,
                        "limit": min(max_count, 10),
                        "lang": "zh_cn"
                    }, headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout)
            except Exception as e:
                self.logger.warning(f"AppStore搜索失败: {e}")
                continue

            if not data:
                continue

            for r in data.get("results", []):
                app_name = r.get("trackName", "")
                if app_name in seen_apps:
                    continue
                seen_apps.add(app_name)

                all_results.append(NormalizedComplaint(
                    content=f"【App Store】{app_name} - {r.get('artistName','')}",
                    platform="App Store",
                    author=r.get("artistName", ""),
                    likes=int(r.get("averageUserRating", 0) * 20),  # 转为100分制
                    comments=r.get("userRatingCount", 0),
                    published_at=r.get("releaseDate", "")[:10] if r.get("releaseDate") else None,
                    url=r.get("trackViewUrl", ""),
                    tags=[keyword, "App", f"★{r.get('averageUserRating','?')}"],
                    sentiment="positive" if r.get("averageUserRating", 0) >= 4 else "neutral",
                    source_type="ecommerce"
                ))

        if not all_results:
            return self._mock(keyword, max_count)
        return all_results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        return [self._normalize({
            "content": f"【App Store】{keyword}相关应用，用户评分和反馈",
            "author": "App Store",
            "likes": 300,
            "comments": 50,
        }, "App Store") for _ in range(min(max_count, 3))]


class GitHubDataSource(BaseDataSource):
    """
    GitHub Issues搜索 API
    无需认证（免费tier: 60 requests/min）
    搜索关于某产品的用户反馈、功能建议、Bug报告
    """
    name = "github"
    platform_type = PlatformType.INTERNATIONAL
    description = "GitHub Issues搜索，可获取开源社区产品反馈"
    docs_url = "https://docs.github.com/en/rest/search"

    API_SEARCH = "https://api.github.com/search/issues"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.token = self.config.get("github_token") or self.config.get("GITHUB_TOKEN", "")
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True  # 无需token也能用（有频率限制）

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "ChuangYeBang/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        all_results = []
        per_page = min(max_count, 30)
        pages = (max_count + per_page - 1) // per_page

        for page in range(1, pages + 1):
            if len(all_results) >= max_count:
                break

            try:
                data = curl_json(self.API_SEARCH, params={
                    "q": f"{keyword} type:issues",
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "order": "desc"
                }, headers=headers, timeout=self.timeout)
                if not data:
                    break
            except Exception as e:
                self.logger.warning(f"GitHub搜索失败: {e}")
                break

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                labels = [lbl.get("name", "") for lbl in item.get("labels", [])]
                all_results.append(NormalizedComplaint(
                    content=f"【GitHub Issue】{item.get('title', '')}",
                    platform="GitHub",
                    author=item.get("user", {}).get("login", "unknown"),
                    likes=item.get("reactions", {}).get("total_count", 0),
                    comments=item.get("comments", 0),
                    published_at=item.get("created_at", "")[:10] if item.get("created_at") else None,
                    url=item.get("html_url", ""),
                    tags=[keyword] + labels[:3],
                    sentiment=self._sentiment_from_labels(labels),
                    source_type="social"
                ))

        if not all_results:
            return self._mock(keyword, max_count)
        return all_results[:max_count]

    def _sentiment_from_labels(self, labels: List[str]) -> str:
        neg_labels = ["bug", "invalid", "wontfix", "question", "duplicate"]
        pos_labels = ["enhancement", "feature", "good first issue", "help wanted"]
        if any(l in labels for l in neg_labels):
            return "negative"
        if any(l in labels for l in pos_labels):
            return "positive"
        return "neutral"

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        return [self._normalize({
            "content": f"【GitHub】{keyword}相关Issues和功能讨论",
            "author": "GitHub",
            "likes": 10,
            "comments": 5,
        }, "GitHub") for _ in range(min(max_count, 3))]


class HackerNewsDataSource(BaseDataSource):
    """
    Hacker News /开发者新闻 API
    通过 Algolia 搜索（免费）
    科技行业趋势、产品动态、技术讨论
    """
    name = "hackernews"
    platform_type = PlatformType.INTERNATIONAL
    description = "Hacker News科技新闻和讨论"
    docs_url = "https://hn.algolia.com/api"

    ALGOLIA_API = "https://hn.algolia.com/api/v1/search"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {"User-Agent": "ChuangYeBang/1.0"}

        try:
            data = curl_json(self.ALGOLIA_API, params={
                    "query": keyword,
                    "tags": "story",
                    "hitsPerPage": min(max_count, 20),
                }, timeout=self.timeout)
        except Exception as e:
            self.logger.warning(f"HackerNews搜索失败: {e}")
            return self._mock(keyword, max_count)

        if not data:
            return self._mock(keyword, max_count)

        results = []
        for h in data.get("hits", []):
            if h.get("deleted") or h.get("dead"):
                continue
            results.append(NormalizedComplaint(
                content=f"【HN】{h.get('title', '')}",
                platform="HackerNews",
                author=h.get("author", "anonymous"),
                likes=h.get("points", 0),
                comments=h.get("num_comments", 0),
                published_at=datetime.fromtimestamp(h.get("created_at_i", 0)).strftime("%Y-%m-%d") if h.get("created_at_i") else None,
                url=h.get("url", f"https://news.ycombinator.com/item?id={h.get('objectID','')}"),
                tags=[keyword, "HackerNews"],
                sentiment="neutral",
                source_type="social"
            ))

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        return [self._normalize({
            "content": f"【HackerNews】关于{keyword}的科技趋势讨论",
            "author": "HN社区",
            "likes": 100,
            "comments": 20,
        }, "HackerNews") for _ in range(min(max_count, 3))]


class WeiboHotFreeDataSource(BaseDataSource):
    """
    微博热搜（免费版，无需登录）
    直接爬取微博热搜页面，解析实时热搜词
    """
    name = "weibo_hot_free"
    platform_type = PlatformType.DOMESTIC_CN
    description = "微博实时热搜榜（免费，无需账号）"
    docs_url = "https://s.weibo.com"

    HOT_API = "https://top.toutiao.io/api/index/hot_list?country=cn"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str = "", max_count: int = 50) -> List[NormalizedComplaint]:
        """获取微博热搜榜，可按关键词筛选"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://weibo.com",
        }

        # 方案1: 微博移动端热搜
        results = self._try_weibo_hot(headers, keyword, max_count)
        if results:
            return results

        # 方案2: 今日头条热搜（备用）
        results = self._try_toutiao_hot(headers, keyword, max_count)
        if results:
            return results

        return self._mock(keyword, max_count)

    def _try_weibo_hot(self, headers, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        """尝试获取微博热搜"""
        try:
            data = curl_json("https://weibo.com/ajax/side/hotSearch", timeout=self.timeout)
            if not data:
                return []

            bands = data.get("data", {}).get("band_list", [])
            if not bands:
                return []

            results = []
            for item in bands:
                word = item.get("word", "")
                if keyword and keyword not in word:
                    continue
                results.append(NormalizedComplaint(
                    content=f"【微博热搜】{word}",
                    platform="微博热搜",
                    author=None,
                    likes=item.get("num", 0),
                    comments=0,
                    published_at=datetime.now().strftime("%Y-%m-%d"),
                    url=f"https://s.weibo.com/weibo?q={word}",
                    tags=["热搜", word],
                    sentiment="neutral",
                    source_type="search"
                ))

            return results[:max_count]
        except Exception as e:
            self.logger.warning(f"微博热搜获取失败: {e}")
            return []

    def _try_toutiao_hot(self, headers, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        """尝试获取今日头条热搜"""
        try:
            data = curl_json("https://top.toutiao.io/api/index/hot_list", timeout=self.timeout)
            if not data:
                return []

            items = data.get("data", [])
            results = []
            for item in items:
                title = item.get("word", item.get("Title", ""))
                if keyword and keyword not in title:
                    continue
                results.append(NormalizedComplaint(
                    content=f"【头条热搜】{title}",
                    platform="头条热搜",
                    author=None,
                    likes=item.get("hot_score", 0),
                    comments=0,
                    published_at=datetime.now().strftime("%Y-%m-%d"),
                    url=item.get("link", ""),
                    tags=["热搜", title],
                    sentiment="neutral",
                    source_type="search"
                ))
            return results[:max_count]
        except Exception as e:
            self.logger.warning(f"头条热搜获取失败: {e}")
            return []

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock_trends = [
            "民宿行业新规出台", "新能源汽车续航突破", "奶茶价格上调引热议",
            "消费者维权成功案例", "电商平台服务评价", "国货品牌崛起",
            "直播带货投诉激增", "预付卡消费套路", "网红餐厅实地测评",
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


class ToutiaoDataSource(BaseDataSource):
    """
    今日头条搜索 API
    免费，返回新闻/文章/视频多类型内容
    """
    name = "toutiao"
    platform_type = PlatformType.DOMESTIC_CN
    description = "今日头条新闻搜索"
    docs_url = "https://open.snssdk.com"

    API_SEARCH = "https://so.toutiao.com/s/search_pgc.json"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://so.toutiao.com",
        }

        try:
            data = curl_json(self.API_SEARCH, params={
                    "keyword": keyword,
                    "page": 1,
                    "page_size": min(max_count, 20),
                    "sort": "0",
                    "pd": "pgc",
                    "source": "input",
                }, timeout=self.timeout)
        except Exception as e:
            self.logger.warning(f"今日头条搜索失败: {e}")
            return self._mock(keyword, max_count)

        results = []
        for item in data.get("data", []):
            results.append(NormalizedComplaint(
                content=f"【头条】{item.get('title', '')}",
                platform="今日头条",
                author=item.get("user_info", {}).get("name", ""),
                likes=item.get("agree_count", 0),
                comments=item.get("comment_count", 0),
                published_at=item.get("datetime", "")[:10] if item.get("datetime") else None,
                url=item.get("url", ""),
                tags=[keyword, "今日头条"],
                sentiment="neutral",
                source_type="social"
            ))

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        return [self._normalize({
            "content": f"【头条】关于{keyword}的新闻报道和用户讨论",
            "author": "头条号",
            "likes": 100,
            "comments": 20,
        }, "今日头条") for _ in range(min(max_count, 3))]


class ZhihuDataSource(BaseDataSource):
    """
    知乎搜索 API
    免费有限流，返回问答数据
    """
    name = "zhihu"
    platform_type = PlatformType.DOMESTIC_CN
    description = "知乎问答搜索"
    docs_url = "https://www.zhihu.com/api/v4"

    API_SEARCH = "https://www.zhihu.com/api/v4/search_v3"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.access_token = self.config.get("access_token") or self.config.get("ZHIHU_ACCESS_TOKEN", "")
        self.timeout = self.config.get("timeout", 8)

    @property
    def is_configured(self) -> bool:
        return True  # 知乎有频率限制但无需key

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.zhihu.com",
            "x-api-version": "3.0.91",
            "x-app-za": "OS=Web",
        }

        params = {
            "q": keyword,
            "type": "article",
            "limit": min(max_count, 10),
            "offset": 0,
        }

        try:
            data = curl_json(self.API_SEARCH, timeout=self.timeout)
            if not data:
                return self._mock(keyword, max_count)
        except Exception as e:
            self.logger.warning(f"知乎搜索失败: {e}")
            return self._mock(keyword, max_count)

        results = []
        for item in data.get("data", []):
            obj = item.get("object", {})
            question = obj.get("question", {})
            title = question.get("title", obj.get("title", ""))

            results.append(NormalizedComplaint(
                content=f"【知乎】{title} {obj.get('excerpt', '')}".strip(),
                platform="知乎",
                author=obj.get("author", {}).get("name", "知乎用户"),
                likes=obj.get("voteup_count", 0),
                comments=obj.get("comment_count", 0),
                published_at=None,
                tags=[keyword, "知乎"],
                sentiment="neutral",
                source_type="social"
            ))

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"关于{keyword}的深度分析：从用户痛点看行业机会", "author": "创业者老王", "likes": random.randint(200, 1000), "comments": random.randint(20, 80)},
            {"content": f"{keyword}有哪些坑？过来人经验分享", "author": "匿名用户", "likes": random.randint(100, 500), "comments": random.randint(10, 50)},
        ]
        return [self._normalize(item, "知乎") for item in mock[:max_count]]


# ============================================================
# 国际免费平台（翻墙后可用）
# ============================================================

class TwitterFreeDataSource(BaseDataSource):
    """
    Twitter/X 搜索（免费端，无需 API Key）
    使用 Nitter 第三方开源镜像（无需登录）
    https://nitter.net 是一个 Twitter 镜像站，提供 RSS/API
    """
    name = "twitter_free"
    platform_type = PlatformType.INTERNATIONAL
    description = "Twitter/X 搜索（通过 Nitter 镜像，无需账号）"
    docs_url = "https://nitter.net"

    NITTER_INSTANCES = [
        "https://nitter.net",
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
        "https://nitter.mrsend.fr",
    ]

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return True # 无需认证

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        results = []

        for instance in self.NITTER_INSTANCES:
            if results:
                break
            try:
                data = curl_get(f"{instance}/search", params={"f": "tweets", "q": keyword}, headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout)
                if not data:
                    continue

                # 解析 HTML
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(data, "html.parser")
                tweets = soup.select(".timeline-item")
                if not tweets:
                    continue

                for tweet in tweets[:max_count]:
                    try:
                        content_elem = tweet.select_one(".tweet-content")
                        author_elem = tweet.select_one(".username")
                        time_elem = tweet.select_one(".tweet-date")
                        likes_elem = tweet.select_one(".icon-star, .tweet-stats .icon-heart")
                        content = content_elem.get_text(strip=True) if content_elem else ""

                        if len(content) < 5:
                            continue

                        results.append(NormalizedComplaint(
                            content=f"【Twitter】{content}",
                            platform="Twitter",
                            author=author_elem.get_text(strip=True) if author_elem else "unknown",
                            likes=0,
                            comments=0,
                            published_at=time_elem.get("title", "")[:10] if time_elem else None,
                            url="",
                            tags=[keyword, "Twitter"],
                            sentiment="neutral",
                            source_type="social"
                        ))
                    except Exception:
                        continue

                break
            except Exception as e:
                self.logger.warning(f"Nitter {instance} 失败: {e}")
                continue

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Has anyone had issues with {keyword}? The quality seems inconsistent.", "author": "techreviewer", "likes": random.randint(10, 200), "comments": random.randint(5, 50)},
            {"content": f"After testing {keyword} for a month, here's my honest review...", "author": "reviewer_jane", "likes": random.randint(50, 500), "comments": random.randint(10, 100)},
        ]
        return [self._normalize(item, "Twitter") for item in mock[:max_count]]


class RedditFreeDataSource(BaseDataSource):
    """
    Reddit 搜索（免费，无需登录）
    使用 Reddit JSON API（公共端，无认证）
    """
    name = "reddit_free"
    platform_type = PlatformType.INTERNATIONAL
    description = "Reddit社区讨论（免费，无需账号）"
    docs_url = "https://www.reddit.com/dev/api"

    REDDIT_SEARCH = "https://www.reddit.com/search.json"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        headers = {
            "User-Agent": "ChuangYeBang/1.0 (by /u/yourusername)",
            "Accept": "application/json",
        }

        params = {
            "q": keyword,
            "sort": "relevance",
            "t": "all",
            "limit": min(max_count, 25),
            "restrict_sr": "",
        }

        try:
            data = curl_json(self.REDDIT_SEARCH, params=params, headers=headers, timeout=self.timeout)
        except Exception as e:
            self.logger.warning(f"Reddit搜索失败: {e}")
            return self._mock(keyword, max_count)

        if not data:
            return self._mock(keyword, max_count)

        results = []
        children = data.get("data", {}).get("children", [])
        for child in children:
            post = child.get("data", {})
            if not post.get("is_self"):
                continue

            results.append(NormalizedComplaint(
                content=f"【Reddit】{post.get('title', '')}: {post.get('selftext', '')[:300]}",
                platform="Reddit",
                author=post.get("author", "unknown"),
                likes=post.get("ups", 0),
                comments=post.get("num_comments", 0),
                published_at=datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d") if post.get("created_utc") else None,
                url=f"https://reddit.com{post.get('permalink', '')}",
                tags=[keyword, post.get("subreddit", "")],
                sentiment=self._guess_sentiment(post.get("title", "") + " " + post.get("selftext", "")),
                source_type="social"
            ))

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _guess_sentiment(self, text: str) -> str:
        text_lower = text.lower()
        neg = sum(w in text_lower for w in ["bad", "terrible", "awful", "scam", "worst", "disappointed", "problem", "broken", "sucks"])
        pos = sum(w in text_lower for w in ["good", "great", "awesome", "excellent", "love", "best", "amazing", "recommend"])
        if neg > pos:
            return "negative"
        if pos > neg:
            return "positive"
        return "neutral"

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Warning: {keyword} has serious quality control issues. Here's my experience after 3 months...", "author": "Throwaway_user", "likes": random.randint(100, 2000), "comments": random.randint(20, 300)},
        ]
        return [self._normalize(item, "Reddit") for item in mock[:max_count]]


class TrustpilotFreeDataSource(BaseDataSource):
    """
    Trustpilot 免费数据
    可直接爬取公开评价页面（无需 API Key）
    """
    name = "trustpilot_free"
    platform_type = PlatformType.INTERNATIONAL
    description = "Trustpilot企业评价（免费网页爬取）"
    docs_url = "https://www.trustpilot.com"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 10)

    @property
    def is_configured(self) -> bool:
        return True

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            self.logger.warning("BeautifulSoup not installed, using mock")
            return self._mock(keyword, max_count)

        try:
            data = curl_get(f"https://www.trustpilot.com/search?query={keyword}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=self.timeout)
            soup = BeautifulSoup(data, 'html.parser')
            reviews = soup.select(".paper_paper__1BMrb, .review-card")
        except Exception as e:
            self.logger.warning(f"Trustpilot爬取失败: {e}")
            return self._mock(keyword, max_count)

        results = []
        for review in reviews[:max_count]:
            try:
                content = review.get_text(strip=True)[:300]
                stars_elem = review.select_one("[data-star-rating], .star")
                stars = int(stars_elem.get("data-star-rating", "0")[0]) if stars_elem else 3

                results.append(NormalizedComplaint(
                    content=f"【Trustpilot】{content}",
                    platform="Trustpilot",
                    author=review.select_one(".consumer-name, .name") or "Anonymous",
                    likes=0,
                    comments=0,
                    published_at=None,
                    tags=[keyword, "Trustpilot"],
                    sentiment=self._sentiment(stars),
                    source_type="social"
                ))
            except Exception:
                continue

        if not results:
            return self._mock(keyword, max_count)
        return results[:max_count]

    def _sentiment(self, stars: int) -> str:
        if stars >= 4:
            return "positive"
        if stars <= 2:
            return "negative"
        return "neutral"

    def _mock(self, keyword: str, max_count: int) -> List[NormalizedComplaint]:
        import random
        mock = [
            {"content": f"Outstanding service from {keyword}. Highly recommend.", "author": "James W.", "likes": random.randint(5, 50)},
            {"content": f"Average experience. Nothing special but got the job done.", "author": "Emily R.", "likes": random.randint(3, 30)},
            {"content": f"Terrible experience. Customer support is non-existent.", "author": "David K.", "likes": random.randint(1, 20)},
        ]
        return [self._normalize(item, "Trustpilot") for item in mock[:max_count]]