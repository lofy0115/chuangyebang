"""
统一数据源插件接口
所有数据源（微博API、国际平台爬虫、电商等）都实现此接口

使用方式:
    from app.datasources import get_datasource_manager

    mgr = get_datasource_manager()
    mgr.enable("weibo")  # 启用微博数据源
    results = mgr.search("民宿", max_count=50)  # 从所有启用源搜索
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import random


class PlatformType(Enum):
    DOMESTIC_CN = "domestic_cn"       # 中国平台（微博、知乎等）
    INTERNATIONAL = "international"   # 国际平台（Twitter/X、Reddit等）
    ECOMMERCE_CN = "ecommerce_cn"     # 中国电商（京东、淘宝等）
    ECOMMERCE_INT = "ecommerce_int"   # 国际电商（亚马逊等）
    COMPLAINT = "complaint"           # 投诉平台（黑猫、12315等）


@dataclass
class NormalizedComplaint:
    """所有数据源返回的统一格式"""
    content: str                          # 文本内容
    platform: str                         # 平台名
    author: Optional[str] = None          # 作者/用户
    likes: int = 0                        # 点赞数
    comments: int = 0                     # 评论数
    shares: int = 0                       # 分享/转发数
    published_at: Optional[str] = None    # 发布时间 YYYY-MM-DD
    url: Optional[str] = None             # 原文链接
    tags: List[str] = field(default_factory=list)   # 标签
    sentiment: str = "neutral"            # 情感: positive/negative/neutral
    source_type: str = "social"           # social/ecommerce/complaint/search


class BaseDataSource(ABC):
    """数据源插件基类，所有数据源必须继承此类"""

    # --- 类属性子类必须覆盖 ---
    name: str = "base"
    platform_type: PlatformType = PlatformType.DOMESTIC_CN
    description: str = ""
    docs_url: str = ""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"datasource.{self.name}")
        self._enabled = False

    @abstractmethod
    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        """
        核心方法：搜索关键词，返回标准化数据列表
        """
        pass

    def health_check(self) -> bool:
        """健康检查，子类可重写"""
        try:
            self.search("测试", max_count=1)
            return True
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False

    def _normalize(self, raw: Dict, platform: str) -> NormalizedComplaint:
        """将原始数据规范化为统一格式"""
        return NormalizedComplaint(
            content=raw.get("content", raw.get("text", raw.get("title", ""))),
            platform=platform,
            author=raw.get("author", raw.get("user", raw.get("username"))),
            likes=raw.get("likes", raw.get("favorite_count", raw.get("up_count", 0))),
            comments=raw.get("comments", raw.get("reply_count", raw.get("comment_count", 0))),
            shares=raw.get("shares", raw.get("retweet_count", raw.get("share_count", 0))),
            published_at=raw.get("published_at", raw.get("created_at", raw.get("time"))),
            url=raw.get("url", raw.get("link")),
            tags=raw.get("tags", []),
            sentiment=raw.get("sentiment", "neutral"),
            source_type=self.platform_type.value
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} type={self.platform_type.value}>"


class MockDataSource(BaseDataSource):
    """Mock数据源 - 开发/测试用"""
    name = "mock"
    platform_type = PlatformType.DOMESTIC_CN
    description = "内置mock数据，用于开发测试"
    docs_url = ""

    MOCK_DATA = {
        "新能源汽车": [
            {"content": "续航虚标严重，标称500公里实际只能跑350公里，冬天更惨只有250", "author": "新能源车主123", "likes": 234, "comments": 89, "sentiment": "negative"},
            {"content": "充电桩太少，出去一趟找充电桩比开车时间还长，焦虑症都犯了", "author": "电车车主小明", "likes": 189, "comments": 67, "sentiment": "negative"},
            {"content": "售后服务太差，有问题推来推去，修了3次还没修好", "author": "匿名用户", "likes": 156, "comments": 45, "sentiment": "negative"},
            {"content": "保费每年涨，比燃油车贵多了，成本太高", "author": "老司机", "likes": 123, "comments": 34, "sentiment": "negative"},
            {"content": "贬值太快，买了一年贬值40%，二手车商都不收", "author": "车主老王", "likes": 98, "comments": 23, "sentiment": "negative"},
            {"content": "车机系统经常死机，导航用着用着就黑屏，太危险了", "author": "科技迷", "likes": 87, "comments": 19, "sentiment": "negative"},
            {"content": "维修费用离谱，一个小刮蹭修一下要好几千，换电池更是天价", "author": "车主阿东", "likes": 76, "comments": 12, "sentiment": "negative"},
            {"content": "等了三个月才交车，订金交了也不能退，感觉被套住了", "author": "等等党", "likes": 65, "comments": 8, "sentiment": "negative"},
        ],
        "民宿": [
            {"content": "图片和实际差太多，到了才发现被坑，退款难", "author": "旅行爱好者", "likes": 267, "comments": 98, "sentiment": "negative"},
            {"content": "卫生堪忧，床单没换，房间有异味，根本没法住", "author": "民宿住客", "likes": 234, "comments": 87, "sentiment": "negative"},
            {"content": "位置偏僻，导航找不到，晚上黑灯瞎火的太不安全", "author": "游客甲", "likes": 189, "comments": 67, "sentiment": "negative"},
            {"content": "隔音太差，隔壁说话听得一清二楚，吵得睡不着", "author": "睡眠浅的人", "likes": 156, "comments": 45, "sentiment": "negative"},
            {"content": "客服永远联系不上，出问题找不到人解决", "author": "出差族", "likes": 134, "comments": 34, "sentiment": "negative"},
        ],
        "奶茶": [
            {"content": "价格越来越贵，一杯奶茶动辄30多，感觉被收智商税", "author": "奶茶爱好者", "likes": 312, "comments": 134, "sentiment": "negative"},
            {"content": "糖量不可选，全是标准糖，太甜了根本喝不下去", "author": "减肥中", "likes": 234, "comments": 89, "sentiment": "negative"},
            {"content": "店员态度差，催单就翻白眼，流水线作业没有服务可言", "author": "消费者", "likes": 189, "comments": 67, "sentiment": "negative"},
            {"content": "卫生问题堪忧，制作过程不透明，原料来源不清楚", "author": "食品安全关注者", "likes": 167, "comments": 45, "sentiment": "negative"},
            {"content": "等一杯奶茶要30分钟，排队时间太长效率太低", "author": "上班族", "likes": 145, "comments": 34, "sentiment": "negative"},
        ],
    }

    def search(self, keyword: str, max_count: int = 50) -> List[NormalizedComplaint]:
        # 精确匹配优先
        for kw, items in self.MOCK_DATA.items():
            if kw in keyword or keyword in kw:
                selected = random.sample(items, min(max_count, len(items)))
                return [self._normalize(item, self.name) for item in selected]
        # 默认返回新能源汽车数据
        items = random.sample(self.MOCK_DATA["新能源汽车"], min(max_count, 5))
        return [self._normalize(item, self.name) for item in items]

    def _normalize(self, raw: Dict, platform: str) -> NormalizedComplaint:
        return NormalizedComplaint(
            content=raw["content"],
            platform=platform,
            author=raw.get("author"),
            likes=raw.get("likes", 0),
            comments=raw.get("comments", 0),
            published_at=None,
            sentiment=raw.get("sentiment", "neutral"),
            source_type="social"
        )