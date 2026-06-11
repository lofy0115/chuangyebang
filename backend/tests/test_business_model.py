import pytest
from app.services import BusinessModelService, AnalysisService

def test_generate_lean_canvas():
    service = BusinessModelService()
    # 模拟分析结果
    analysis_result = {
        "industry": "母婴",
        "complaint_distribution": [
            {"type": "性能问题", "count": 35, "percentage": 35.0},
            {"type": "价格问题", "count": 28, "percentage": 28.0},
            {"type": "功能缺失", "count": 22, "percentage": 22.0},
            {"type": "服务体验", "count": 15, "percentage": 15.0}
        ],
        "customer_segments": [
            {"segment": "价格敏感型", "needs": ["便宜", "优惠", "划算"]},
            {"segment": "品质优先型", "needs": ["质量", "高端", "品牌"]}
        ]
    }
    canvas = service.generate_lean_canvas(analysis_result)
    assert "problem" in canvas
    assert "solution" in canvas
    assert "unique_value_proposition" in canvas
    assert canvas["problem"][0]["title"] == "性能问题"

def test_generate_business_model_canvas():
    service = BusinessModelService()
    analysis_result = {"industry": "母婴"}
    canvas = service.generate_business_model_canvas(analysis_result)
    assert "customer_segments" in canvas
    assert "value_propositions" in canvas
    assert "channels" in canvas
    assert len(canvas) == 9

def test_calculate_model_score():
    service = BusinessModelService()
    canvas = {
        "problem": [{"title": "test"}],
        "solution": [{"title": "test"}],
        "unique_value_proposition": "test value prop",
        "unfair_advantage": "test advantage",
        "key_metrics": ["metric1"],
        "channels": ["channel1"],
        "cost_structure": "test cost",
        "revenue_streams": "test revenue"
    }
    score = service.calculate_model_score(canvas)
    assert score >= 0 and score <= 100

def test_get_canvas_types():
    service = BusinessModelService()
    # 通过API测试
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/api/canvas/types")
    assert response.status_code == 200
    assert len(response.json()["types"]) == 3

def test_generate_canvas_via_api():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.post("/api/canvas/generate", json={"keyword": "母婴", "canvas_type": "lean"})
    assert response.status_code == 200
    data = response.json()
    assert "canvas" in data
    assert "completeness_score" in data
    assert data["canvas_type"] == "lean"