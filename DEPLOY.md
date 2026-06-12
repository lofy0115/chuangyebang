# 创业帮 - 服务器部署指南

## 推荐服务器配置

### 🏆 最推荐：阿里云香港/腾讯云香港
- **优势**：中国大陆访问速度快 + 可访问微博/小红书/京东
- **价格**：约 30-50 元/月
- **配置**：1核2G即可，爬虫不占多少内存

### 备选：DigitalOcean 新加坡
- **价格**：约 20 美元/月
- **配置**：2核4G

---

## 快速部署（全新服务器）

### 1. 安装 Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 一键部署
```bash
# 克隆代码
git clone https://github.com/lofy0115/chuangyebang.git
cd chuangyebang

# 启动服务
docker-compose up -d --build

# 检查状态
docker-compose ps
docker-compose logs -f backend
```

### 3. 验证服务
```bash
curl http://localhost:8000/api/workflow/health
# 期望输出: {"status":"ok","services":{"scraper":"ready",...}}

# 访问 API 文档
curl http://localhost:8000/docs
```

---

## 数据爬取平台一览

部署到有中国大陆网络的服务器后，爬虫可访问以下平台：

| 平台 | 类型 | 数据量 | 覆盖内容 |
|------|------|--------|---------|
| **微博** | 社交媒体 | 海量 | 用户抱怨、品牌投诉、产品质量 |
| **微博热搜** | 热搜榜单 | 每日实时 | 全网热点话题 |
| **小红书** | 种草社区 | 海量 | 用户体验、真实评价、产品吐槽 |
| **京东** | 电商评论 | 百万级 | 商品差评、追评、问答 |
| **淘宝** | 电商评论 | 百万级 | 商品评论、问大家 |
| **黑猫投诉** | 投诉平台 | 专项 | 消费者维权、欺诈举报 |
| **消费保** | 投诉平台 | 专项 | 售后维权、霸王条款 |
| **12315** | 官方投诉 | 专项 | 官方维权数据 |

---

## 数据采集策略

### 广度优先
- **关键词策略**：每个行业生成50+相关关键词（品牌词、品类词、场景词、问题词）
- **多平台并行**：同时爬取6+平台，避免单一来源偏差
- **时间跨度**：覆盖近2年数据，捕捉趋势变化

### 客观性保障
- **来源交叉验证**：同一问题在3+平台出现才视为真实痛点
- **情感分析**：区分"质量问题"、"个人偏好"、"恶意差评"
- **热度权重**：按点赞/评论数加权，高互动内容更有代表性

---

## 添加更多数据源

如需增加数据源，在 `backend/app/scrapers/` 目录下创建新的爬虫文件：

```python
# backend/app/scrapers/baidu_scraper.py
from .base_scraper import BaseScraper

class BaiduScraper(BaseScraper):
    PLATFORM_NAME = "百度"

    def scrape(self, keyword: str, max_count: int = 100) -> List[Dict]:
        # 实现爬取逻辑
        ...
```

然后在 `scraper_manager.py` 的 `SCRAPERS` 字典中注册即可。

---

## 监控与维护

### 查看爬虫日志
```bash
docker-compose logs -f backend | grep -i scraper
```

### 重启服务
```bash
docker-compose restart backend
```

### 更新代码
```bash
git pull
docker-compose up -d --build
```