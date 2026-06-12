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
    """标准分析接口 - 任意关键词都可分析，返回智能分类结果和高价值痛点"""
    if not request.keyword or len(request.keyword.strip()) < 2:
        raise HTTPException(status_code=400, detail="关键词长度至少2个字符")

    service = AnalysisService()
    result = service.analyze_industry(request.keyword.strip())
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
        result = collect_and_analyze_sync(request.keyword.strip(), max_per_source=100)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"深度分析失败: {str(e)}")

@router.get("/data-sources")
def get_data_sources():
    """获取支持的数据源列表"""
    from app.datasources.datasource_manager import DataSourceManager
    mgr = DataSourceManager()
    raw = mgr.get_all()
    sources = [
        {
            "id": k,
            "name": v.name,
            "type": getattr(v, 'type', 'unknown'),
            "enabled": getattr(v, 'enabled', True),
        }
        for k, v in raw.items()
    ]
    return {
        "sources": sources,
        "total": len(sources),
        "note": "免费数据源无需认证可直接使用，付费/API数据源需要配置相应凭证"
    }