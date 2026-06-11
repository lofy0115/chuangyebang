from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import VectorService

router = APIRouter()
_service = VectorService()

class AddComplaintsRequest(BaseModel):
    complaints: List[dict]

class FindSimilarRequest(BaseModel):
    query: str
    top_k: int = 10

class ClusterRequest(BaseModel):
    n_clusters: int = 8

@router.post("/vector/add")
def add_complaints(request: AddComplaintsRequest):
    """添加抱怨记录到向量库"""
    count = _service.add_complaints(request.complaints)
    return {"added": count, "total_in_library": len(_service.vectors)}

@router.post("/vector/find-similar")
def find_similar(request: FindSimilarRequest):
    """查找相似抱怨"""
    if not _service.vectors:
        raise HTTPException(status_code=400, detail="向量库为空，请先添加抱怨数据")
    results = _service.find_similar(request.query, request.top_k)
    return {"query": request.query, "results": results}

@router.post("/vector/cluster")
def cluster_complaints(request: ClusterRequest):
    """对抱怨进行聚类分析"""
    if len(_service.vectors) < request.n_clusters:
        raise HTTPException(status_code=400, detail=f"数据量({len(_service.vectors)})少于聚类数({request.n_clusters})")
    clusters = _service.cluster_complaints(request.n_clusters)
    summary = _service.get_cluster_summary()
    return {"n_clusters": request.n_clusters, "clusters": summary}

@router.get("/vector/opportunities")
def find_opportunities():
    """发现创新机会：高频负面+低频正面=改进空间大"""
    opportunities = _service.find_innovation_opportunities()
    return {"opportunities": opportunities}

@router.get("/vector/stats")
def get_stats():
    """获取向量库统计"""
    return {
        "total_vectors": len(_service.vectors),
        "clusters_summary": _service.get_cluster_summary()[:5]
    }

@router.post("/vector/reset")
def reset_library():
    """清空向量库"""
    _service.reset()
    return {"message": "向量库已清空"}