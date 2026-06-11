"""
爬虫集成服务 - 将多源数据聚合与NLP分析整合
这是创业帮的核心数据管道：
多源爬虫 -> 数据聚合 -> NLP分析 -> 结构化结果
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from app.spiders.aggregator import DataAggregator
from app.spiders.base_spider import BaseSpider
from .nlp_service import NLPService


class SpiderIntegrationService:
    """
    爬虫集成服务
    协调多源爬虫数据收集与NLP分析，提供统一的分析接口
    """
    
    def __init__(self):
        self.aggregator = DataAggregator()
        self.nlp_service = NLPService()
    
    async def collect_and_analyze(self, keyword: str, max_per_source: int = 100) -> Dict:
        """
        核心方法：从多源收集数据并进行NLP分析
        
        流程：
        1. 从所有可用渠道并行收集数据
        2. 合并去重
        3. 对每条数据进行NLP分析（情感、分类、关键词）
        4. 聚合统计（类型分布、客户细分、价值需求）
        """
        # Step 1: 多源并行收集
        data_by_source = await self.aggregator.collect_all(keyword, max_per_source)
        
        # Step 2: 获取收集统计
        stats = self.aggregator.get_statistics(data_by_source)
        
        # Step 3: 合并去重
        all_data = self.aggregator.merge_and_deduplicate(data_by_source)
        
        # Step 4: NLP分析每条数据
        analyzed_data = []
        for item in all_data:
            content = item.get("content", "")
            if content:
                nlp_result = self.nlp_service.analyze_text(content)
                item["nlp_analysis"] = nlp_result
                item["sentiment"] = nlp_result.get("sentiment", 0)
                item["complaint_type"] = nlp_result.get("complaint_type", "其他")
                item["keywords"] = nlp_result.get("keywords", [])
            analyzed_data.append(item)
        
        # Step 5: 聚合统计
        aggregated = self._aggregate_results(analyzed_data, keyword)
        aggregated["data_sources"] = stats
        aggregated["sample_data"] = analyzed_data[:20]  # 返回样本
        
        return aggregated
    
    def _aggregate_results(self, analyzed_data: List[Dict], keyword: str) -> Dict:
        """聚合分析结果"""
        total = len(analyzed_data)
        
        # 抱怨类型分布
        complaint_counts = {}
        sentiment_sum = 0
        for item in analyzed_data:
            ct = item.get("complaint_type", "其他")
            complaint_counts[ct] = complaint_counts.get(ct, 0) + 1
            sentiment_sum += item.get("sentiment", 0)
        
        complaint_distribution = [
            {"type": ct, "count": count, "percentage": round(count / total * 100, 1)}
            for ct, count in sorted(complaint_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # 情感统计
        avg_sentiment = sentiment_sum / total if total > 0 else 0
        
        # 价值需求提取（按情感强度和频次）
        top_value_needs = self._extract_value_needs(analyzed_data)
        
        # 客户细分
        customer_segments = self._segment_customers(analyzed_data)
        
        # 数据源覆盖统计
        source_coverage = {}
        for item in analyzed_data:
            source = item.get("source", "unknown")
            if source not in source_coverage:
                source_coverage[source] = {"count": 0, "avg_sentiment": 0, "sentiment_sum": 0}
            source_coverage[source]["count"] += 1
            source_coverage[source]["sentiment_sum"] += item.get("sentiment", 0)
        
        for source, data in source_coverage.items():
            data["avg_sentiment"] = round(data["sentiment_sum"] / data["count"], 2) if data["count"] > 0 else 0
            data["percentage"] = round(data["count"] / total * 100, 1)
        
        return {
            "industry": keyword,
            "total_records": total,
            "avg_sentiment": round(avg_sentiment, 2),
            "complaint_distribution": complaint_distribution,
            "top_value_needs": top_value_needs,
            "customer_segments": customer_segments,
            "source_coverage": source_coverage,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _extract_value_needs(self, analyzed_data: List[Dict]) -> List[Dict]:
        """提取高价值需求（正面情感+高频）"""
        needs_map = {}
        for item in analyzed_data:
            sentiment = item.get("sentiment", 0)
            if sentiment > 0:  # 正面反馈 -> 潜在价值需求
                keywords = item.get("keywords", [])
                for kw in keywords[:3]:
                    if kw not in needs_map:
                        needs_map[kw] = {"need": kw, "count": 0, "priority": 0}
                    needs_map[kw]["count"] += 1
                    needs_map[kw]["priority"] += sentiment
        
        sorted_needs = sorted(needs_map.values(), key=lambda x: x["priority"], reverse=True)[:10]
        for i, need in enumerate(sorted_needs):
            need["priority"] = min(100, max(1, int(need["priority"] / max(1, need["count"]))))
        
        return sorted_needs
    
    def _segment_customers(self, analyzed_data: List[Dict]) -> List[Dict]:
        """客户细分"""
        segments = {
            "价格敏感型": {"needs": [], "count": 0},
            "品质优先型": {"needs": [], "count": 0},
            "尝鲜体验型": {"needs": [], "count": 0},
            "实用主义型": {"needs": [], "count": 0}
        }
        
        for item in analyzed_data:
            sentiment = item.get("sentiment", 0)
            complaint_type = item.get("complaint_type", "")
            
            if complaint_type == "价格问题":
                segments["价格敏感型"]["count"] += 1
            elif sentiment > 2:
                segments["品质优先型"]["count"] += 1
            elif item.get("source") in ["小红书", "抖音"]:
                segments["尝鲜体验型"]["count"] += 1
            else:
                segments["实用主义型"]["count"] += 1
        
        result = []
        total = len(analyzed_data)
        for seg_name, data in segments.items():
            if data["count"] > 0:
                result.append({
                    "segment": seg_name,
                    "count": data["count"],
                    "percentage": round(data["count"] / total * 100, 1)
                })
        
        return sorted(result, key=lambda x: x["count"], reverse=True)


# 同步包装器，方便API调用
def collect_and_analyze_sync(keyword: str, max_per_source: int = 100) -> Dict:
    """同步版本的collect_and_analyze"""
    service = SpiderIntegrationService()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(service.collect_and_analyze(keyword, max_per_source))