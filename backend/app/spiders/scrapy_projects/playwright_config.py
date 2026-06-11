"""
Playwright配置 - 用于动态页面爬取
当Scrapy无法处理JavaScript渲染的页面时使用Playwright
"""
from playwright.sync_api import sync_playwright, Browser, BrowserContext
from typing import Optional

class PlaywrightHelper:
    """Playwright辅助类 - 处理动态页面"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def new_context(self, user_agent: str = None) -> BrowserContext:
        """创建新的浏览器上下文"""
        context = self.browser.new_context(
            user_agent=user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        return context

    def scroll_and_wait(self, page, scroll_pause_time: float = 1.0, max_scrolls: int = 5):
        """滚动页面加载更多内容"""
        for _ in range(max_scrolls):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(scroll_pause_time * 1000)

    def fetch_dynamic_page(self, url: str, wait_selector: str = None) -> Optional[str]:
        """获取动态页面的HTML内容"""
        context = self.new_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle")
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=10000)

            self.scroll_and_wait(page)

            return page.content()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
        finally:
            page.close()
            context.close()

def example_usage():
    with PlaywrightHelper(headless=True) as helper:
        html = helper.fetch_dynamic_page(
            "https://www.xiaohongshu.com/search_result?keyword=母婴",
            wait_selector=".note-item"
        )
        if html:
            print(f"Got HTML content length: {len(html)}")