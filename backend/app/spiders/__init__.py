from .base_spider import BaseSpider
from .e_commerce_spiders import TaobaoSpider, JDSpider, PinduoduoSpider
from .social_spiders import WeiboSpider, XiaohongshuSpider, ZhihuSpider, DouyinSpider
from .forum_spiders import BaiduTiebaSpider, HupuSpider, RedditSpider
from .complaint_spiders import HeimaoComplaintSpider, Consumer12315Spider, TianyanchaComplaintSpider
from .aggregator import DataAggregator

__all__ = [
    "BaseSpider",
    "TaobaoSpider",
    "JDSpider",
    "PinduoduoSpider",
    "WeiboSpider",
    "XiaohongshuSpider",
    "ZhihuSpider",
    "DouyinSpider",
    "BaiduTiebaSpider",
    "HupuSpider",
    "RedditSpider",
    "HeimaoComplaintSpider",
    "Consumer12315Spider",
    "TianyanchaComplaintSpider",
    "DataAggregator",
]