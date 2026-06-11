import scrapy
import re

class WeiboSearchSpider(scrapy.Spider):
    """
    微博搜索爬虫 - 需要微博开放平台API权限
    文档: https://open.weibo.com/wiki/API
    """
    name = "weibo_search"
    allowed_domains = ["weibo.com", "sina.com.cn"]

    def __init__(self, keyword=None, max_results=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.max_results = int(max_results)

    def start_requests(self):
        url = f"https://s.weibo.com/weibo?q={self.keyword}"
        yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        """解析微博搜索页"""
        self.logger.info(f"Parsing weibo search: {response.url}")

        weibo_cards = response.xpath("//div[@class=card-feed]")
        for card in weibo_cards[:self.max_results]:
            content = card.xpath(".//p[@class=txt]//text()").getall()
            user = card.xpath(".//a[@class=name]//text()").get()

            yield {
                "id": card.xpath("@mid").get() or "",
                "source": "微博",
                "content": "".join(content).strip(),
                "user_nick": user or "",
                "reposts_count": int(card.xpath(".//a[@action-type=转发]/@count").get() or 0),
                "likes_count": int(card.xpath(".//span[@class=woo-like-count]//text()").get() or 0),
                "created_at": card.xpath(".//a[@class=date]//text()").get() or ""
            }

def main():
    """命令行入口"""
    from scrapy.cmdline import execute
    execute(["scrapy", "crawl", "weibo_search"])