"""
数据源管理器 - 统一调度所有数据源插件
"""
from typing import List, Dict, Optional, Set
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_datasource import BaseDataSource, NormalizedComplaint, PlatformType, MockDataSource
from .weibo_datasource import WeiboDataSource, WeiboHotSearchDataSource, ZhihuDataSource
from .international_datasource import TwitterDataSource, RedditDataSource, AmazonReviewsDataSource, TrustpilotDataSource
from .free_datasource import (
    BilibiliDataSource, CSDNDataSource, AppStoreDataSource, GitHubDataSource,
    HackerNewsDataSource, WeiboHotFreeDataSource, ToutiaoDataSource, ZhihuDataSource as ZhihuDataSourceFree,
    TwitterFreeDataSource, RedditFreeDataSource, TrustpilotFreeDataSource
)


class DataSourceManager:
    """
    数据源管理器
    支持:
    - 插件式注册/注销数据源
    - 并发多源搜索
    - 按平台类型筛选
    - Mock兜底
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger("datasource_manager")
        self._sources: Dict[str, BaseDataSource] = {}
        self._enabled: Set[str] = set()
        self._init_builtin_sources()

    def _init_builtin_sources(self):
        """初始化内置数据源"""
        # ===== 无需认证的免费数据源（开箱即用）=====
        # 国内免费平台
        self.register(BilibiliDataSource(self.config))      # B站视频搜索
        self.register(CSDNDataSource(self.config))            # CSDN技术文章
        self.register(WeiboHotFreeDataSource(self.config))    # 微博热搜
        self.register(ToutiaoDataSource(self.config))         # 今日头条
        self.register(ZhihuDataSourceFree(self.config))       # 知乎

        # 国际免费平台
        self.register(GitHubDataSource(self.config))          # GitHub Issues
        self.register(HackerNewsDataSource(self.config)) # Hacker News
        self.register(AppStoreDataSource(self.config))        # App Store
        self.register(RedditFreeDataSource(self.config))     # Reddit

        # ===== 需要认证的 API 数据源 =====
        # 国内平台（需微博开放平台账号）
        self.register(WeiboDataSource(self.config))
        self.register(WeiboHotSearchDataSource(self.config))

        # 国际平台（翻墙后可用）
        self.register(TwitterFreeDataSource(self.config))    # Twitter镜像（免费）
        self.register(TwitterDataSource(self.config))         # Twitter API v2（需Bearer Token）
        self.register(TrustpilotFreeDataSource(self.config))  # Trustpilot（免费爬取）

        # ===== 需要额外配置的数据源 =====
        self.register(AmazonReviewsDataSource(self.config))
        self.register(TrustpilotDataSource(self.config))

        # Mock兜底（始终最后兜底）
        self.register(MockDataSource(self.config))
        self._enabled.discard("mock")
        self._enabled.add("mock")

        # 默认启用：所有 is_configured=True 的数据源
        # 但排除已知需要翻墙或网络不稳定的数据源
        vpn_required = {"reddit_free", "twitter_free", "trustpilot_free", "twitter", "amazon", "trustpilot"}
        for name, src in self._sources.items():
            if name == "mock":
                continue
            if hasattr(src, "is_configured"):
                if src.is_configured and name not in vpn_required:
                    self._enabled.add(name)
                    self.logger.info(f"已启用数据源: {name} ({src.platform_type.value})")
            else:
                self._enabled.add(name)

    def register(self, source: BaseDataSource):
        """注册数据源"""
        self._sources[source.name] = source
        self.logger.info(f"注册数据源: {source.name} ({source.platform_type.value})")

    def enable(self, name: str):
        """启用指定数据源"""
        if name in self._sources:
            self._enabled.add(name)
            self.logger.info(f"启用数据源: {name}")

    def disable(self, name: str):
        """禁用指定数据源"""
        self._enabled.discard(name)
        self.logger.info(f"禁用数据源: {name}")

    def get_enabled(self) -> List[str]:
        """获取已启用数据源列表"""
        return list(self._enabled)

    def get_all(self) -> Dict[str, BaseDataSource]:
        """获取所有数据源"""
        return dict(self._sources)

    def get_by_type(self, platform_type: PlatformType) -> List[BaseDataSource]:
        """按类型筛选数据源"""
        return [s for s in self._sources.values() if s.platform_type == platform_type]

    def search(
        self,
        keyword: str,
        max_count: int = 50,
        platforms: Optional[List[str]] = None,
        timeout: float = 15.0,
        use_parallel: bool = True
    ) -> List[NormalizedComplaint]:
        """
        从多个数据源搜索

        Args:
            keyword: 搜索关键词
            max_count: 最大结果数
            platforms: 指定平台列表（None=所有已启用平台）
            timeout: 超时时间（秒）
            use_parallel: 是否并发搜索
        """
        # 确定要搜索的数据源
        if platforms:
            target_sources = [self._sources[p] for p in platforms if p in self._sources]
        else:
            target_sources = [self._sources[n] for n in self._enabled if n in self._sources]

        if not target_sources:
            self.logger.warning("没有可用数据源，使用 mock")
            return self._sources["mock"].search(keyword, max_count)

        all_results = []
        seen_contents = set()  # 去重

        if use_parallel:
            # 并发搜索（限制并发数以避免子进程冲突）
            with ThreadPoolExecutor(max_workers=min(len(target_sources), 4)) as executor:
                futures = {
                    executor.submit(src.search, keyword, max_count): src.name
                    for src in target_sources
                }

                try:
                    for future in as_completed(futures, timeout=timeout):
                        src_name = futures[future]
                        try:
                            results = future.result()
                            for r in results:
                                # 内容去重（取前60字）
                                key = r.content[:60]
                                if key and key not in seen_contents:
                                    seen_contents.add(key)
                                    all_results.append(r)
                        except Exception as e:
                            self.logger.warning(f"数据源 {src_name} 出错: {e}")
                except Exception as e:
                    self.logger.warning(f"并发搜索超时或出错: {e}")
        else:
            # 串行搜索
            for src in target_sources:
                try:
                    results = src.search(keyword, max_count)
                    for r in results:
                        key = r.content[:60]
                        if key and key not in seen_contents:
                            seen_contents.add(key)
                            all_results.append(r)
                except Exception as e:
                    self.logger.warning(f"数据源 {src.name} 出错: {e}")

        # 确保至少有一些数据
        if len(all_results) < 3:
            self.logger.info("数据不足，使用 mock 补充")
            mock_results = self._sources["mock"].search(keyword, max_count)
            for r in mock_results:
                key = r.content[:60]
                if key and key not in seen_contents:
                    seen_contents.add(key)
                    all_results.append(r)

        self.logger.info(f"数据源搜索完成: {keyword}, 共 {len(all_results)} 条来自 {len(target_sources)} 个平台")
        return all_results[:max_count]

    def health_check_all(self) -> Dict[str, bool]:
        """检查所有数据源健康状态（只测 is_configured，不发网络请求）"""
        results = {}
        for name, src in self._sources.items():
            # 只检查是否已配置，不发网络请求（避免超时）
            results[name] = getattr(src, 'is_configured', True)
        return results

    def get_stats(self) -> Dict:
        """获取数据源统计信息"""
        return {
            "total": len(self._sources),
            "enabled": len(self._enabled),
            "by_type": {
                pt.value: len([s for s in self._sources.values() if s.platform_type == pt])
                for pt in PlatformType
            },
            "sources": {
                name: {
                    "type": src.platform_type.value,
                    "enabled": name in self._enabled,
                    "configured": getattr(src, "is_configured", True),
                    "description": src.description,
                }
                for name, src in self._sources.items()
            }
        }


# 全局单例
_datasource_manager: Optional[DataSourceManager] = None


def get_datasource_manager() -> DataSourceManager:
    global _datasource_manager
    if _datasource_manager is None:
        import os
        config = {
            "WEIBO_APP_KEY": os.getenv("WEIBO_APP_KEY", ""),
            "WEIBO_ACCESS_TOKEN": os.getenv("WEIBO_ACCESS_TOKEN", ""),
            "ZHIHU_ACCESS_TOKEN": os.getenv("ZHIHU_ACCESS_TOKEN", ""),
            "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN", ""),
            "RAPIDAPI_KEY": os.getenv("RAPIDAPI_KEY", ""),
            "TRUSTPILOT_API_KEY": os.getenv("TRUSTPILOT_API_KEY", ""),
            "TRUSTPILOT_BUSINESS_UNIT": os.getenv("TRUSTPILOT_BUSINESS_UNIT", ""),
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        }
        _datasource_manager = DataSourceManager(config)
    return _datasource_manager