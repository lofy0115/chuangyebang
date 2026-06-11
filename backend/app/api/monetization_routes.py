from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import MonetizationService, AnalysisService

router = APIRouter()

class RecommendRequest(BaseModel):
    keyword: str

class EstimateRequest(BaseModel):
    model_key: str
    avg_price: float = 100
    customer_count: int = 1000
    retention_rate: float = 0.8
    margin: float = 0.5
    cac: float = 300

class ForecastRequest(BaseModel):
    model_key: str
    avg_price: float = 100
    customer_count: int = 1000
    retention_rate: float = 0.8
    margin: float = 0.5
    cac: float = 300
    months: int = 12

@router.get("/profit-models")
def list_models():
    """列出所有利润模式"""
    service = MonetizationService()
    templates = service.get_profit_model_templates()
    return {
        "models": [
            {"id": k, "name": v.get("name", k), "description": v.get("description", "")}
            for k, v in templates.items()
        ]
    }

@router.get("/profit-models/{model_key}")
def get_model(model_key: str):
    """获取模式详情"""
    service = MonetizationService()
    detail = service.get_single_model_template(model_key)
    if not detail:
        raise HTTPException(status_code=404, detail="未找到该模式")
    return detail

@router.post("/profit-models/recommend")
def recommend_models(request: RecommendRequest):
    """基于分析结果推荐利润模式"""
    service = MonetizationService()
    analysis_service = AnalysisService()
    analysis = analysis_service.analyze_industry(request.keyword)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"未找到「{request.keyword}」的分析结果")
    recommendations = service.recommend_model(analysis)
    return {"industry": request.keyword, "recommendations": recommendations}

@router.post("/profit-models/estimate")
def estimate_unit_economics(request: EstimateRequest):
    """估算单位经济模型"""
    service = MonetizationService()
    params = {
        "avg_price": request.avg_price,
        "customer_count": request.customer_count,
        "retention_rate": request.retention_rate,
        "margin": request.margin,
        "cac": request.cac
    }
    result = service.calculate_unit_economics(request.model_key, params)
    return result

@router.post("/profit-models/forecast")
def forecast_revenue(request: ForecastRequest):
    """收入预测"""
    service = MonetizationService()
    params = {
        "avg_price": request.avg_price,
        "customer_count": request.customer_count,
        "retention_rate": request.retention_rate,
        "margin": request.margin,
        "cac": request.cac
    }
    result = service.forecast_revenue(request.model_key, params, request.months)
    return {
        "model_key": request.model_key,
        "projection": result
    }