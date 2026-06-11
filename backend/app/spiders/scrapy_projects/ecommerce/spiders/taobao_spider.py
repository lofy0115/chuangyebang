import scrapy
import json
import time
from datetime import datetime

class TaobaoCommentSpider(scrapy.Spider):
    """
    淘宝评论爬虫 - 需要淘宝开放平台API权限
    文档: https://open.taobao.com/docs.htm?docId=116
    """
    name = "taobao_comments"
    allowed_domains = ["taobao.com", "tmall.com"]

    def __init__(self, item_id=None, keyword=None, max_pages=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        self.keyword = keyword
        self.max_pages = int(max_pages)
        self.results = []

    def start_requests(self):
        if self.item_id:
            url = f"https://detail.tmall.com/item.htm?id={self.item_id}"
            yield scrapy.Request(url, callback=self.parse_item_page, meta={"item_id": self.item_id})
        elif self.keyword:
            url = f"https://s.taobao.com/search?q={self.keyword}"
            yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        """解析搜索结果页"""
        self.logger.info(f"Parsing search page: {response.url}")
        item_ids = response.xpath("//@data-id").getall()
        for item_id in item_ids[:self.max_pages]:
            yield scrapy.Request(
                f"https://detail.tmall.com/item.htm?id={item_id}",
                callback=self.parse_item_page,
                meta={"item_id": item_id}
            )

    def parse_item_page(self, response):
        """解析商品详情页"""
        item_id = response.meta.get("item_id", "")

        comments = self._fetch_comments_via_api(item_id)
        for comment in comments:
            yield {
                "id": f"taobao_{comment.get('id', '')}",
                "source": "淘宝",
                "content": comment.get("content", ""),
                "user_nick": comment.get("userNick", ""),
                "rate_date": comment.get("rateDate", ""),
                "platform": "mobile" if "html5" in response.url else "pc",
                "sentiment": 0,
                "created_at": datetime.now().isoformat()
            }

    def _fetch_comments_via_api(self, item_id):
        """通过淘宝API获取评论（需要权限）"""
        return []

def main():
    """命令行入口"""
    from scrapy.cmdline import execute
    execute(["scrapy", "crawl", "taobao_comments"])