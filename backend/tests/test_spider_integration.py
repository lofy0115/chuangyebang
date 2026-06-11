import pytest
import asyncio
from app.services import SpiderIntegrationService, collect_and_analyze_sync
from app.spiders.aggregator import DataAggregator


@pytest.mark.asyncio
async def test_spider_integration_collect():
    """测试多源数据收集"""
    service = SpiderIntegrationService()
    result = await service.collect_and_analyze("母婴", max_per_source=50)
    
    assert "total_records" in result
    assert "data_sources" in result
    assert result["total_records"] > 0
    assert result["industry"] == "母婴"

@pytest.mark.asyncio
async def test_data_sources_coverage():
    """测试数据源覆盖"""
    service = SpiderIntegrationService()
    result = await service.collect_and_analyze("智能家居", max_per_source=30)
    
    # 应该从多个数据源收集数据
    assert result["total_records"] > 0
    assert "source_coverage" in result

def test_sync_wrapper():
    """测试同步包装器"""
    result = collect_and_analyze_sync("美妆", max_per_source=30)
    assert "total_records" in result
    assert result["total_records"] > 0

def test_data_aggregator_weights():
    """测试数据源权重配置"""
    agg = DataAggregator()
    total_weight = sum(DataAggregator.SOURCE_WEIGHTS.values())
    assert total_weight > 0  # 权重和应该大于0
    assert len(DataAggregator.SOURCE_WEIGHTS) >= 10  # 至少10个数据源

def test_get_data_sources_api():
    """测试数据源API"""
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/api/data-sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_deep_analyze_api():
    """测试深度分析API"""
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.post("/api/analyze/deep", json={"keyword": "新能源汽车"})
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "source_coverage" in data