from fastapi import APIRouter, HTTPException
from app.services import NLPService, AnalysisService, SpiderIntegrationService, collect_and_analyze_sync
from app.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "message": "创业帮API服务正常运行"}

@router.get("/complaint-types")
def get_complaint_types():
    service = AnalysisService()
    return {"complaint_types": service.get_complaint_types()}

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_industry(request: AnalyzeRequest):
    """标准分析接口（使用模拟数据，快速响应）"""
    if not request.keyword or len(request.keyword.strip()) < 2:
        raise HTTPException(status_code=400, detail="关键词长度至少2个字符")

    service = AnalysisService()
    result = service.analyze_industry(request.keyword)

    if result is None:
        raise HTTPException(status_code=404, detail=f"未找到与「{request.keyword}」相关的行业数据")

    return result

@router.post("/analyze/deep")
def analyze_industry_deep(request: AnalyzeRequest):
    """
    深度分析接口（使用多源爬虫，数据更全面但响应较慢）
    从10+个数据源收集数据：电商、社交媒体、论坛、投诉平台等
    """
    if not request.keyword or len(request.keyword.strip()) < 2:
        raise HTTPException(status_code=400, detail="关键词长度至少2个字符")

    try:
        result = collect_and_analyze_sync(request.keyword, max_per_source=100)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"深度分析失败: {str(e)}")

@router.get("/data-sources")
def get_data_sources():
    """
    获取支持的数据源列表及权重配置
    这是创业帮数据客观性的核心：多源交叉验证
    """
    from app.spiders.aggregator import DataAggregator
    agg = DataAggregator()

    sources = []
    for name, weight in DataAggregator.SOURCE_WEIGHTS.items():
        spider_class = DataAggregator.SPIDER_REGISTRY.get(name)
        status = "active" if spider_class else "planned"
        sources.append({
            "id": name,
            "weight": weight,
            "status": status,
            "description": "已接入" if status == "active" else "规划中"
        })

    return {
        "sources": sources,
        "total_weight": sum(s["weight"] for s in sources),
        "note": "数据权重反映该来源的可信度和客观性，投诉平台权重较高因为抱怨强度真实"
    }