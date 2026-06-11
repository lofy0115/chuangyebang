"""
数据聚合器 - 将多个数据源整合
这是创业帮的核心：从多个渠道收集消费者反馈，确保数据广度和客观性
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from .base_spider import BaseSpider
from .e_commerce_spiders import TaobaoSpider, JDSpider, PinduoduoSpider
from .social_spiders import WeiboSpider, XiaohongshuSpider, ZhihuSpider, DouyinSpider
from .forum_spiders import BaiduTiebaSpider, HupuSpider, RedditSpider
from .complaint_spiders import HeimaoComplaintSpider, Consumer12315Spider, TianyanchaComplaintSpider


class DataAggregator:
    """
    数据聚合器 - 从多个渠道收集评论数据
    确保数据来源的：广度（多平台）、多样性（不同类型）、客观性（正负面均衡）
    """

    SPIDER_REGISTRY = {
        "taobao": TaobaoSpider,
        "jd": JDSpider,
        "pinduoduo": PinduoduoSpider,
        "weibo": WeiboSpider,
        "xiaohongshu": XiaohongshuSpider,
        "zhihu": ZhihuSpider,
        "douyin": DouyinSpider,
        "baidu_tieba": BaiduTiebaSpider,
        "hupu": HupuSpider,
        "reddit": RedditSpider,
        "heimao": HeimaoComplaintSpider,
        "12315": Consumer12315Spider,
        "tianyancha": TianyanchaComplaintSpider,
    }

    SOURCE_WEIGHTS = {
        "taobao": 0.15,
        "jd": 0.15,
        "pinduoduo": 0.10,
        "weibo": 0.10,
        "xiaohongshu": 0.08,
        "zhihu": 0.10,
        "douyin": 0.08,
        "baidu_tieba": 0.05,
        "hupu": 0.03,
        "reddit": 0.02,
        "heimao": 0.12,
        "12315": 0.12,
        "tianyancha": 0.05,
    }

    def __init__(self):
        self.spiders = {}
        self._init_spiders()

    def _init_spiders(self):
        """初始化所有可用的爬虫"""
        for name, spider_class in self.SPIDER_REGISTRY.items():
            if spider_class:
                self.spiders[name] = spider_class()

    async def collect_all(self, keyword: str, max_per_source: int = 100) -> Dict[str, List[Dict]]:
        """
        从所有可用渠道收集数据
        返回：{source_name: [comments]}
        """
        tasks = []
        source_names = []
        for name, spider in self.spiders.items():
            if spider:
                tasks.append(self._collect_from_source(name, spider, keyword, max_per_source))
                source_names.append(name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated = {}
        for i, name in enumerate(source_names):
            if i < len(results) and not isinstance(results[i], Exception):
                aggregated[name] = results[i]

        return aggregated

    async def _collect_from_source(self, name: str, spider: BaseSpider, keyword: str, max_results: int) -> List[Dict]:
        """从单个数据源收集"""
        try:
            data = await spider.search(keyword, max_results)
            return data
        except Exception as e:
            print(f"收集{name}数据失败: {e}")
            return []

    def merge_and_deduplicate(self, data_by_source: Dict[str, List[Dict]]) -> List[Dict]:
        """
        合并并去重
        按权重和质量综合排序
        """
        all_data = []
        for source, data_list in data_by_source.items():
            weight = self.SOURCE_WEIGHTS.get(source, 0.05)
            for item in data_list:
                item["source"] = source
                item["weight"] = weight
                all_data.append(item)

        all_data.sort(key=lambda x: x.get("weight", 0) * (x.get("likes", 0) + 1), reverse=True)

        seen = set()
        unique_data = []
        for item in all_data:
            content_key = item.get("content", "")[:50]
            if content_key not in seen:
                seen.add(content_key)
                unique_data.append(item)

        return unique_data

    def get_statistics(self, data_by_source: Dict[str, List[Dict]]) -> Dict:
        """获取数据收集统计"""
        total = sum(len(data) for data in data_by_source.values())
        return {
            "total_records": total,
            "sources_covered": len(data_by_source),
            "by_source": {source: len(data) for source, data in data_by_source.items()},
            "timestamp": datetime.now().isoformat()
        }