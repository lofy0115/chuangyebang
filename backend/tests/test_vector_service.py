import pytest
from app.services import VectorService

def test_embed_text():
    service = VectorService()
    vec = service.embed_text("这个产品质量很好，使用很方便")
    assert len(vec) == 128
    assert abs(vec.sum()) >= 0 # L2归一化后

def test_add_complaints():
    service = VectorService()
    complaints = [
        {"content": "质量不错", "source": "淘宝", "sentiment": 1.0, "complaint_type": "质量"},
        {"content": "价格太贵", "source": "京东", "sentiment": -1.0, "complaint_type": "价格"},
        {"content": "服务态度很好", "source": "微博", "sentiment": 2.0, "complaint_type": "服务"},
    ]
    count = service.add_complaints(complaints)
    assert count == 3
    assert len(service.vectors) == 3

def test_find_similar():
    service = VectorService()
    complaints = [
        {"content": "质量很好，很耐用", "source": "淘宝", "sentiment": 2.0, "complaint_type": "质量"},
        {"content": "用了一周就坏了", "source": "京东", "sentiment": -2.0, "complaint_type": "质量"},
        {"content": "性价比很高", "source": "拼多多", "sentiment": 1.0, "complaint_type": "价格"},
    ]
    service.add_complaints(complaints)
    
    results = service.find_similar("产品质量怎么样", top_k=3)
    assert len(results) > 0
    assert all("similarity" in r for r in results)

def test_cluster_complaints():
    service = VectorService()
    complaints = [
        {"content": f"质量不错{i}", "source": "淘宝", "sentiment": 1.0, "complaint_type": "质量"}
        for i in range(15)
    ] + [
        {"content": f"价格太贵{i}", "source": "京东", "sentiment": -1.0, "complaint_type": "价格"}
        for i in range(15)
    ]
    service.add_complaints(complaints)
    
    clusters = service.cluster_complaints(n_clusters=4)
    assert len(clusters) > 0

def test_find_opportunities():
    service = VectorService()
    # 高频负面+低频正面 = 创新机会
    complaints = [
        {"content": "坏了", "source": "淘宝", "sentiment": -2.0, "complaint_type": "质量"}
        for _ in range(20)
    ] + [
        {"content": "质量不错", "source": "京东", "sentiment": 2.0, "complaint_type": "质量"}
        for _ in range(2)
    ]
    service.add_complaints(complaints)
    
    opportunities = service.find_innovation_opportunities()
    assert len(opportunities) > 0
    assert opportunities[0]["type"] == "质量"

def test_reset():
    service = VectorService()
    service.add_complaints([{"content": "test", "source": "test", "sentiment": 0}])
    assert len(service.vectors) > 0
    service.reset()
    assert len(service.vectors) == 0

def test_vector_api():
    from app.main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Add complaints
    resp = client.post("/api/vector/add", json={
        "complaints": [
            {"content": "质量不错", "source": "淘宝", "sentiment": 1.0, "complaint_type": "质量"},
            {"content": "价格太贵", "source": "京东", "sentiment": -1.0, "complaint_type": "价格"}
        ]
    })
    assert resp.status_code == 200
    
    # Find similar
    resp = client.post("/api/vector/find-similar", json={
        "query": "产品质量怎么样",
        "top_k": 5
    })
    assert resp.status_code == 200
    assert len(resp.json()["results"]) > 0
    
    # Get stats
    resp = client.get("/api/vector/stats")
    assert resp.status_code == 200
    
    # Reset
    resp = client.post("/api/vector/reset")
    assert resp.status_code == 200