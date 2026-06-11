# Scrapy Projects

真实爬虫框架集成Scrapy + Playwright配置

## 目录结构

```
scrapy_projects/
├── setup.py                    # 项目安装脚本
├── config.yaml                 # 配置文件
├── playwright_config.py # Playwright动态页面配置
├── ecommerce/
│   └── spiders/
│       ├── taobao_spider.py    # 淘宝评论爬虫
│       └── jd_spider.py # 京东评论爬虫
└── social/
    └── spiders/
        └── weibo_spider.py     # 微博搜索爬虫
```

## 安装

```bash
cd scrapy_projects
pip install -e .
```

## 使用方法

### 淘宝爬虫

```bash
scrapy crawl taobao_comments -a item_id=123456789
scrapy crawl taobao_comments -a keyword=手机 -a max_pages=10
```

### 京东爬虫

```bash
scrapy crawl jd_comments -a sku_id=123456
scrapy crawl jd_comments -a keyword=电脑 -a max_pages=10
```

### 微博爬虫

```bash
scrapy crawl weibo_search -a keyword=科技 -a max_results=100
```

## Playwright动态页面

当Scrapy无法处理JavaScript渲染的页面时，使用PlaywrightHelper：

```python
from playwright_config import PlaywrightHelper

with PlaywrightHelper(headless=True) as helper:
    html = helper.fetch_dynamic_page(
        "https://example.com",
        wait_selector=".content"
    )
```

## 配置说明

编辑 `config.yaml` 修改：
- Scrapy请求配置
- 代理IP池
- 平台请求频率限制

## 注意事项

1. 淘宝、京东、微博平台需要相应的API权限
2. 请遵守平台的robots.txt规则
3. 注意请求频率限制，避免封禁
4. 部分页面需要登录态，使用Playwright处理