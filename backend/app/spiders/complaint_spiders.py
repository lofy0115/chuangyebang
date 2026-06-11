from typing import List, Dict
from datetime import datetime
from .base_spider import BaseSpider

class HeimaoComplaintSpider(BaseSpider):
    """黑猫投诉爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "黑猫投诉"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"hm_{i}",
                "source": "黑猫投诉",
                "content": f"投诉{keyword}质量问题，商家不处理",
                "complaint_level": "high" if i % 2 == 0 else "medium",
                "status": "pending" if i % 2 == 0 else "resolved",
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, complaint_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {"id": f"hm_c_{i}", "content": f"投诉跟进{i}", "跟进状态": "处理中"}
            for i in range(50)
        ]

class Consumer12315Spider(BaseSpider):
    """12315消费者投诉爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "12315"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"12315_{i}",
                "source": "12315",
                "content": f"消费者投诉：{keyword}存在虚假宣传",
                "resolved": i % 3 == 0,
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, complaint_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {"id": f"12315_c_{i}", "content": f"投诉详情{i}", "处理结果": "处理中"}
            for i in range(50)
        ]

class TianyanchaComplaintSpider(BaseSpider):
    """天眼查投诉爬虫"""
    def __init__(self):
        super().__init__()
        self.source = "天眼查"

    async def search(self, keyword: str, max_results: int = 100) -> List[Dict]:
        return [
            {
                "id": f"tyc_{i}",
                "source": "天眼查",
                "content": f"企业投诉：{keyword}涉嫌违规",
                "complaint_type": "工商投诉",
                "status": "pending" if i % 2 == 0 else "investigation",
                "created_at": datetime.now().isoformat()
            }
            for i in range(100)
        ]

    async def get_comments(self, complaint_id: str, max_results: int = 50) -> List[Dict]:
        return [
            {"id": f"tyc_c_{i}", "content": f"投诉详情{i}", "处理状态": "处理中"}
            for i in range(50)
        ]