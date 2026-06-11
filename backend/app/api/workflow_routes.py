"""
完整工作流API - 从搜索到落地路线图的端到端服务
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.scrapers.scraper_manager import ScraperManager
from app.services.ai_analysis_service import AIAnalysisService
from app.services.profit_model_service import ProfitModelService
from app.services.roadmap_service import RoadmapService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflow", tags=["workflow"])


class SearchRequest(BaseModel):
    query: str
    max_results: int = 50


class PainPointSelection(BaseModel):
    pain_point: Dict
    profit_model_key: Optional[str] = None
    custom_params: Optional[Dict] = None


# 全局服务实例
_scraper_manager = None
_ai_service = None
_profit_service = None
_roadmap_service = None


def get_scraper_manager():
    global _scraper_manager
    if _scraper_manager is None:
        _scraper_manager = ScraperManager()
    return _scraper_manager


def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIAnalysisService()
    return _ai_service


def get_profit_service():
    global _profit_service
    if _profit_service is None:
        _profit_service = ProfitModelService()
    return _profit_service


def get_roadmap_service():
    global _roadmap_service
    if _roadmap_service is None:
        _roadmap_service = RoadmapService()
    return _roadmap_service


@router.post("/search")
async def search_complaints(request: SearchRequest):
    """
    Step 1: 搜索消费者抱怨
    输入关键词，爬取各平台真实评论
    """
    try:
        manager = get_scraper_manager()
        logger.info(f"开始搜索: {request.query}")

        # 并发爬取多个平台
        platforms = manager.get_platforms()
        all_complaints = []

        for platform in platforms[:6]:  # 限制平台数量
            try:
                scraper = manager.get_scraper(platform)
                if scraper:
                    results = scraper.scrape(request.query, request.max_results // 6)
                    if results:
                        for r in results:
                            r["source_platform"] = platform
                        all_complaints.extend(results)
            except Exception as e:
                logger.warning(f"平台{platform}爬取失败: {e}")

        # 去重
        seen = set()
        unique_complaints = []
        for c in all_complaints:
            content = c.get("content", "")[:50]
            if content and content not in seen:
                seen.add(content)
                unique_complaints.append(c)

        logger.info(f"爬取完成，共{len(unique_complaints)}条唯一评论")

        return {
            "success": True,
            "query": request.query,
            "total_collected": len(unique_complaints),
            "platforms_used": list(set(c.get("source_platform", "unknown") for c in unique_complaints)),
            "complaints": unique_complaints[:request.max_results]
        }

    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/analyze")
async def analyze_complaints(complaints: List[Dict]):
    """
    Step 2: AI智能分析抱怨
    输入评论列表，输出分类结果+痛点+洞察
    """
    try:
        ai_service = get_ai_service()
        logger.info(f"开始分析{len(complaints)}条评论")

        result = ai_service.analyze_complaints(complaints)

        logger.info(f"分析完成，发现{len(result['pain_points'])}个痛点")

        return {
            "success": True,
            "statistics": result["statistics"],
            "pain_points": result["pain_points"],
            "insights": result["insights"],
            "classified_complaints": result["classified"]
        }

    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/design")
async def design_profit_model(selection: PainPointSelection):
    """
    Step 3: 基于痛点设计利润模式
    输入选中的痛点，输出推荐方案+单位经济+收入预测
    """
    try:
        profit_service = get_profit_service()
        pain_point = selection.pain_point

        logger.info(f"设计利润模式: {pain_point.get('name', '')}")

        # 推荐模式
        rec_result = profit_service.recommend_model(pain_point)
        top_model = rec_result.get("top_recommendation", {})
        model_key = selection.profit_model_key or top_model.get("model", "product_sales")

        # 单位经济计算
        params = selection.custom_params or {}
        unit_econ = profit_service.calculate_unit_economics(model_key, params)

        # 收入预测
        forecast = profit_service.forecast_revenue(model_key, params, months=12)

        # 方案对比
        comparison = profit_service.compare_models(
            pain_point,
            [m["model"] for m in rec_result.get("alternatives", [])] + [model_key]
        )

        return {
            "success": True,
            "pain_point": pain_point.get("name", ""),
            "recommended_model": top_model,
            "selected_model": model_key,
            "model_details": profit_service.MODELS.get(model_key),
            "unit_economics": unit_econ,
            "revenue_forecast": forecast,
            "comparison": comparison
        }

    except Exception as e:
        logger.error(f"设计失败: {e}")
        raise HTTPException(status_code=500, detail=f"设计失败: {str(e)}")


@router.post("/roadmap")
async def generate_roadmap(selection: PainPointSelection):
    """
    Step 4: 生成落地路线图
    输入痛点+利润模式，输出分阶段执行计划
    """
    try:
        profit_service = get_profit_service()
        roadmap_service = get_roadmap_service()

        pain_point = selection.pain_point
        model_key = selection.profit_model_key or "subscription"
        params = selection.custom_params or {}

        profit_model = profit_service.MODELS.get(model_key, profit_service.MODELS["product_sales"])

        logger.info(f"生成路线图: {pain_point.get('name', '')} → {model_key}")

        roadmap = roadmap_service.generate_roadmap(pain_point, {
            "model_key": model_key,
            "model_name": profit_model.name
        }, params)

        summary = roadmap_service.generate_roadmap_summary(roadmap)

        return {
            "success": True,
            "roadmap": roadmap,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"路线图生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"路线图生成失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "services": {
            "scraper": "ready",
            "ai_analysis": "ready",
            "profit_model": "ready",
            "roadmap": "ready"
        }
    }