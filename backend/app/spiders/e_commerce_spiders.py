import asyncio
import httpx
from typing import List, Dict
from datetime import datetime
from .base_spider import BaseSpider

class TaobaoSpider(BaseSpider):
    """淘宝/天猫评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "淘宝"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return self._generate_mock_comments(keyword, "淘宝")

    async def get_comments(self, item_id: str, max_results: int = 50) -> List[Dict]:
        return self._generate_mock_comments(item_id, "淘宝")

    def _generate_mock_comments(self, keyword: str, source: str) -> List[Dict]:
        templates = [
            "质量不错，物流也快，会回购",
            "性价比一般，没有想象中好",
            "客服态度很差，等了很久才回复",
            "包装破损了，产品也损坏了",
            "价格太贵了，不值这个价",
            "很好用，已经购买了多次",
            "功能齐全，符合描述",
            "一般般，没什么特别的"
        ]
        return [
            {
                "id": f"{source}_{i}",
                "source": source,
                "content": templates[i % len(templates)],
                "platform": "mobile" if i % 3 == 0 else "pc",
                "sentiment": 1 if i < 4 else -1,
                "created_at": datetime.now().isoformat()
            }
            for i in range(50)
        ]

class JDSpider(BaseSpider):
    """京东评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "京东"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return self._generate_mock_comments(keyword, "京东")

    async def get_comments(self, item_id: str, max_results: int = 50) -> List[Dict]:
        return self._generate_mock_comments(item_id, "京东")

    def _generate_mock_comments(self, keyword: str, source: str) -> List[Dict]:
        templates = [
            "物流超快，第二天就到了",
            "商品和描述一致，体验不错",
            "售后客服态度恶劣，差评",
            "产品有瑕疵，申请退货中",
            "性价比高，值得购买",
            "包装严实，没有损坏",
            "用了一段时间才来评价",
            "一般般，没有特别惊艳"
        ]
        return [
            {
                "id": f"{source}_{i}",
                "source": source,
                "content": templates[i % len(templates)],
                "platform": "mobile" if i % 2 == 0 else "pc",
                "sentiment": 1 if i < 4 else -1,
                "created_at": datetime.now().isoformat()
            }
            for i in range(50)
        ]

class PinduoduoSpider(BaseSpider):
    """拼多多评论爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "拼多多"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return self._generate_mock_comments(keyword, "拼多多")

    async def get_comments(self, item_id: str, max_results: int = 50) -> List[Dict]:
        return self._generate_mock_comments(item_id, "拼多多")

    def _generate_mock_comments(self, keyword: str, source: str) -> List[Dict]:
        templates = [
            "价格便宜，性价比高",
            "质量一般，这个价格还能接受",
            "物流有点慢，等了一周",
            "产品不错，便宜又好用",
            "有点色差，和图片不太一样",
            "总体还行，会推荐给朋友",
            "价格实惠，东西还行",
            "一分钱一分货"
        ]
        return [
            {
                "id": f"{source}_{i}",
                "source": source,
                "content": templates[i % len(templates)],
                "platform": "mobile",
                "sentiment": 1 if i < 4 else -1,
                "created_at": datetime.now().isoformat()
            }
            for i in range(50)
        ]