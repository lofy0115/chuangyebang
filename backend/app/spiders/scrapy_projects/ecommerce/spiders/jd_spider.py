import scrapy
import json
from datetime import datetime

class JDCommentSpider(scrapy.Spider):
    """
    京东评论爬虫 - 需要京东联盟API或爬虫权限
    文档: https://union.jd.com
    """
    name = "jd_comments"
    allowed_domains = ["jd.com", "jdcloud.com"]

    def __init__(self, sku_id=None, keyword=None, max_pages=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sku_id = sku_id
        self.keyword = keyword
        self.max_pages = int(max_pages)

    def start_requests(self):
        if self.sku_id:
            url = f"https://item.jd.com/{self.sku_id}.html"
            yield scrapy.Request(url, callback=self.parse_item_page)
        elif self.keyword:
            url = f"https://search.jd.com/Search?keyword={self.keyword}&enc=utf-8"
            yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        """解析搜索结果页"""
        sku_ids = response.xpath("//div[@class=gl-i-wrap]/@data-sku").getall()
        for sku_id in sku_ids[:self.max_pages]:
            yield scrapy.Request(
                f"https://item.jd.com/{sku_id}.html",
                callback=self.parse_item_page,
                meta={"sku_id": sku_id}
            )

    def parse_item_page(self, response):
        """解析商品详情页"""
        sku_id = response.meta.get("sku_id", "")
        comments = self._fetch_comments_via_api(sku_id)
        for comment in comments:
            yield {
                "id": f"jd_{comment.get('id', '')}",
                "source": "京东",
                "content": comment.get("content", ""),
                "user_nick": comment.get("userNick", ""),
                "rate_date": comment.get("rateDate", ""),
                "score": comment.get("score", 5),
                "created_at": datetime.now().isoformat()
            }

    def _fetch_comments_via_api(self, sku_id):
        """通过京东API获取评论（需要权限）"""
        return []

def main():
    """命令行入口"""
    from scrapy.cmdline import execute
    execute(["scrapy", "crawl", "jd_comments"])