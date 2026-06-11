import asyncio
import httpx
from typing import List, Dict
from datetime import datetime
from .base_spider import BaseSpider

class WeiboSpider(BaseSpider):
    """微博评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "微博"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return self._generate_mock_posts(keyword)

    async def get_comments(self, post_id: str, max_results: int = 50) -> List[Dict]:
        return self._generate_mock_comments(post_id)

    def _generate_mock_posts(self, keyword: str) -> List[Dict]:
        templates = [
            f"吐槽{kw}的质量问题，用了不到一个月就坏了",
            f"求推荐好用的{kw}，不要广子",
            f"{kw}这个价格也太坑了吧",
            f"终于买到了满意的{kw}，太开心了"
        ]
        kw = keyword
        return [
            {
                "id": f"wb_{i}",
                "source": "微博",
                "content": templates[i % len(templates)],
                "user_verified": i % 3 == 0,
                "reposts_count": i * 10,
                "likes_count": i * 5,
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    def _generate_mock_comments(self, post_id: str) -> List[Dict]:
        return [{"id": f"c_{i}", "content": f"评论{i}", "likes": i*2} for i in range(50)]

class XiaohongshuSpider(BaseSpider):
    """小红书笔记/评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "小红书"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"xhs_{i}",
                "source": "小红书",
                "content": f"小红书笔记关于{keyword}",
                "likes": i * 20,
                "type": "note" if i % 2 == 0 else "review",
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, note_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {"id": f"xhs_c_{i}", "content": f"评论{i}", "likes": i * 3}
            for i in range(50)
        ]

class ZhihuSpider(BaseSpider):
    """知乎问答爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "知乎"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"zh_{i}",
                "source": "知乎",
                "content": f"关于{keyword}的问题讨论{i}",
                "question": True if i % 2 == 0 else False,
                "answers_count": i * 5,
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, item_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {
                "id": f"zh_c_{i}",
                "content": f"知乎回答{i}",
                "votes": i * 10,
                "created_at": datetime.now().isoformat()
            }
            for i in range(50)
        ]

class DouyinSpider(BaseSpider):
    """抖音评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "抖音"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"dy_{i}",
                "source": "抖音",
                "content": f"抖音视频关于{keyword}",
                "likes": i * 100,
                "comments_count": i * 10,
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, video_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {"id": f"dy_c_{i}", "content": f"抖音评论{i}", "likes": i * 5}
            for i in range(50)
        ]