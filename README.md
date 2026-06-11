# 🚀 创业帮 - 从消费者抱怨到商业模式

从消费者抱怨数据中发现创业机会，基于《精益创业》和《商业模式新生代》方法论，帮助创业者完成从痛点发现到商业模式设计的完整旅程。

## 功能特性

- 📡 **13个数据源**：淘宝/京东/拼多多 + 微博/小红书/知乎/抖音 + 贴吧/虎扑/Reddit + 黑猫投诉/12315
- 🤖 **NLP智能分析**：分词、情感分析、抱怨分类（8类）、关键词提取、客户细分
- 🎯 **精益画布**：基于《精益创业》的快速验证框架
- 📋 **商业模式画布**：基于《商业模式新生代》的9宫格画布
- 💎 **价值需求挖掘**：从抱怨中提取高频价值需求
- 💰 **变现模式推荐**：7种利润模式 + 单位经济估算 +收入预测
- 🔬 **向量聚类**：相似抱怨发现 + 创新机会识别
- 📱 **PWA移动端**：可添加到手机主屏幕，离线可用

## 技术架构

```
chuangyebang/
├── backend/ # FastAPI后端
│   ├── app/
│   │   ├── api/          # 4套API路由（17个端点）
│   │   ├── services/     # 6个核心服务
│   │   ├── spiders/      # 多源爬虫框架
│   │   └── models/ # SQLAlchemy模型
│   └── tests/             # 27个测试（全通过）
└── frontend/             # Flutter移动应用
    └── lib/
        ├── screens/       # 5个页面
        ├── widgets/       # 5个组件
        ├── services/      # API服务
        └── models/        # 数据模型
```

## 快速启动

### 后端API

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=/home/fly-s/workspace/chuangyebang/backend \
  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000/docs 查看API文档

### Web演示（离线模式）

直接用浏览器打开 `frontend/standalone.html`，无需网络即可演示。

### WiFi网页App

手机和电脑连接同一WiFi，访问 http://电脑IP:3000

## API端点

| 标签 | 端点 | 功能 |
|------|------|------|
| 分析 | `POST /api/analyze` | 标准行业分析 |
| | `POST /api/analyze/deep` | 深度多源分析 |
| 商业模式 | `POST /api/canvas/generate` | 生成精益/商业模式画布 |
| 向量分析 | `POST /api/vector/find-similar` | 相似抱怨发现 |
| | `GET /api/vector/opportunities` | 创新机会发现 |
| 变现模式 | `POST /api/profit-models/recommend` | 利润模式推荐 |
| | `POST /api/profit-models/estimate` | 单位经济估算 |

## 测试

```bash
cd backend
PYTHONPATH=/home/fly-s/workspace/chuangyebang/backend python3 -m pytest tests/ -v
```

## 构建APK（GitHub Actions自动构建）

### 步骤1：创建GitHub仓库

1. 访问 https://github.com/new 创建新仓库，命名为 `chuangyebang`
2. 不要勾选 "Initialize this repository with a README"

### 步骤2：推送代码

```bash
cd /home/fly-s/workspace/chuangyebang
git remote add origin https://github.com/你的用户名/chuangyebang.git
git branch -M main
git push -u origin main
```

### 步骤3：下载APK

1. 访问你的GitHub仓库页面
2. 点击 **Actions** 标签
3. 等待workflow运行完成（约5-10分钟）
4. 点击最新的workflow run
5. 在 "Artifacts" 部分下载：
   - `release-apk` → 发布版APK（可直接安装）
   - `debug-apk` → 调试版APK

## 项目结构

```
chuangyebang/
├── .github/workflows/flutter-build.yml  # GitHub Actions自动构建
├── backend/
│   ├── app/
│   │   ├── api/ # 4套API路由
│   │   │   ├── routes.py           # 分析API
│   │   │   ├── business_routes.py   # 商业模式API
│   │   │   ├── vector_routes.py # 向量聚类API
│   │   │   └── monetization_routes.py # 变现模式API
│   │   ├── services/                # 核心业务逻辑
│   │   │   ├── nlp_service.py # NLP引擎
│   │   │   ├── analysis_service.py # 行业分析
│   │   │   ├── business_model_service.py # 商业模式画布
│   │   │   ├── spider_integration_service.py # 爬虫集成
│   │   │   ├── vector_service.py    # 向量聚类
│   │   │   └── monetization_service.py # 变现模式
│   │   └── spiders/                 # 多源爬虫框架
│   │       ├── aggregator.py        # 数据聚合器
│   │       ├── base_spider.py       # 爬虫基类
│   │       ├── e_commerce_spiders.py # 电商爬虫
│   │       ├── social_spiders.py     # 社交媒体爬虫
│   │       ├── forum_spiders.py # 论坛爬虫
│   │       ├── complaint_spiders.py # 投诉平台爬虫
│   │       └── scrapy_projects/     # 真实爬虫框架
│   └── tests/                       # 27个测试
└── frontend/                        # Flutter移动应用
    ├── lib/
    │   ├── main.dart
    │   ├── screens/                # 5个页面
    │   ├── widgets/                # 5个组件
    │   ├── services/               # API+Mock数据
    │   ├── models/                 # 数据模型
    │   └── theme/                  # 深色主题
    ├── standalone.html             # 离线演示版（无需网络）
    └── pubspec.yaml
```

## 方法论参考

- 《精益创业》(The Lean Startup) - Eric Ries
- 《商业模式新生代》(Business Model Generation) - Alexander Osterwalder
- 《蓝海战略》(Blue Ocean Strategy) - W. Chan Kim

## License

MIT