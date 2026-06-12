"""
数据源插件包
统一的数据获取层，支持多平台并行搜索

核心接口:
- BaseDataSource: 数据源插件基类
- NormalizedComplaint: 标准化投诉数据格式
- PlatformType: 平台类型枚举
- DataSourceManager: 数据源管理器

内置数据源:
- weibo: 微博开放平台 API（需 access_token）
- weibo_hot: 微博热搜 API（需 access_token）
- zhihu: 知乎搜索
- twitter: Twitter/X API v2（需 bearer_token）
- reddit: Reddit 搜索（无需认证）
- amazon: 亚马逊评论（需 PA-API 或 RapidAPI）
- trustpilot: Trustpilot 评价（需 API key）
- mock: Mock 数据（开发测试用）

使用示例:
    from app.datasources import get_datasource_manager

    mgr = get_datasource_manager()
    results = mgr.search("民宿", max_count=50)
    print(f"共获取 {len(results)} 条数据")

    # 查看所有数据源状态
    stats = mgr.get_stats()
    print(stats)
"""
from .base_datasource import BaseDataSource, NormalizedComplaint, PlatformType, MockDataSource
from .datasource_manager import DataSourceManager, get_datasource_manager

__all__ = [
    "BaseDataSource",
    "NormalizedComplaint",
    "PlatformType",
    "MockDataSource",
    "DataSourceManager",
    "get_datasource_manager",
]