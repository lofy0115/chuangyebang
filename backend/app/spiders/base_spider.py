from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio
import httpx
from datetime import datetime

class BaseSpider(ABC):
    """爬虫基类，定义统一接口"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.source = ""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.rate_limit = 1.0

    @abstractmethod
    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        """搜索并返回评论/帖子列表"""
        pass

    @abstractmethod
    async def get_comments(self, item_id: str, max_results: int = 50) -> List[Dict]:
        """获取评论详情"""
        pass

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        return text.strip()

    async def _fetch_with_retry(self, url: str, client: httpx.AsyncClient, max_retries: int = 3) -> Optional[str]:
        """带重试的HTTP请求"""
        for i in range(max_retries):
            try:
                response = await client.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
            except Exception as e:
                if i == max_retries - 1:
                    return None
                await asyncio.sleep(2 ** i)
        return None