# 创业帮 MVP 规格说明书

## 1. 项目概述

**创业帮 MVP** 是一款面向创业者的商业分析工具，核心功能包括：

- **爬取全网消费者评论**：从主流平台采集用户反馈数据
- **NLP分类分析**：对评论进行中文分词、情感分析，分类统计抱怨类型及占比
- **客户细分**：基于评论数据构建客户画像
- **商业模式辅助设计**：基于精益画布和商业模式画布框架，辅助创业者梳理和设计商业模式

## 2. 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 后端框架 | FastAPI |
| 爬虫 | Scrapy + Playwright |
| NLP | jieba + 情感词典 |
| 数据库 | PostgreSQL + Redis |
| ORM | SQLAlchemy |
| 数据验证 | Pydantic |
| ASGI服务器 | uvicorn |
| 测试 | pytest |

## 3. 目录结构

```
backend/app/
├── api/          # API路由
├── core/          # 核心配置
├── models/        # 数据库模型
├── schemas/       # Pydantic模型
├── services/      # 业务逻辑
└── spiders/       # 爬虫模块
```

## 4. MVP功能范围（Phase 1）

### API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/analyze | 接收关键词，返回分析结果 |
| GET | /api/complaint-types | 获取预设抱怨类型列表 |
| GET | /api/health | 健康检查 |

### 内部服务

- **NLP服务**：中文分词（jieba）、情感分析（情感词典）、抱怨分类
- **爬虫服务**：模拟数据（验证架构）

## 5. 数据模型

### Industry（行业）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 行业名称 |
| created_at | DateTime | 创建时间 |

### ComplaintType（抱怨类型定义）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 抱怨类型名称 |
| description | String | 描述 |
| keywords | List[String] | 关联关键词 |

### ComplaintRecord（抱怨记录）

| 字段 |类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| industry_id | Integer | 关联行业 |
| complaint_type_id | Integer | 关联抱怨类型 |
| sentiment_score | Float | 情感分（-1到1） |
| customer_features | JSON | 客户特征 |
| source | String | 来源平台 |
| content | Text | 原始评论内容 |
| created_at | DateTime | 创建时间 |

### CustomerProfile（客户画像）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| industry_id | Integer | 关联行业 |
| demographics | JSON | 人口统计特征 |
| behavior_patterns | JSON | 行为模式 |
| preferences | JSON | 偏好 |
| created_at | DateTime | 创建时间 |

### AnalysisResult（分析结果聚合）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| industry_id | Integer | 关联行业 |
| keyword | String | 分析关键词 |
| total_comments | Integer | 总评论数 |
| complaint_distribution | JSON | 抱怨类型分布 |
| sentiment_distribution | JSON | 情感分布 |
| top_customer_profiles | JSON | 典型客户画像 |
| analysis_date | DateTime | 分析日期 |

## 6. 验收标准

- [ ] API启动成功，`/api/health` 返回 200
- [ ] `/api/complaint-types` 返回预设 8 类抱怨
- [ ] `/api/analyze?keyword=母婴` 返回分类结果和占比
- [ ] 单元测试覆盖核心 NLP 逻辑

## 7. Phase 2-4 目标

### Phase 2：功能完善
- 集成真实爬虫（Scrapy + Playwright）
- 支持更多平台数据源
- 优化 NLP 分类精度

### Phase 3：商业分析增强
- 精益画布生成器
- 商业模式画布生成器
- 竞品对比分析

### Phase 4：智能化与扩展
- AI 建议生成
- 行业趋势预测
- 多语言支持