"""
向量聚类服务 - 基于Milvus实现相似抱怨发现
用于发现长尾抱怨类型、聚类相似问题、挖掘潜在创新机会
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from datetime import datetime


class VectorService:
    """
    向量聚类服务
    使用文本向量化的方式，将相似内容的评论聚类在一起
    帮助发现：1）长尾抱怨类型 2）相似问题聚类 3）潜在创新机会
    """
    
    CLUSTER_LABELS = {
        "质量可靠": {"keywords": ["质量", "可靠", "耐用", "扎实", "好"], "sentiment": "positive"},
        "性价比高": {"keywords": ["便宜", "划算", "超值", "性价比", "省钱"], "sentiment": "positive"},
        "使用便捷": {"keywords": ["方便", "简单", "容易", "快捷", "一键"], "sentiment": "positive"},
        "外观设计": {"keywords": ["好看", "漂亮", "美观", "颜值", "时尚"], "sentiment": "positive"},
        "服务优质": {"keywords": ["服务好", "态度好", "耐心", "负责"], "sentiment": "positive"},
        "功能齐全": {"keywords": ["功能多", "齐全", "全面", "实用"], "sentiment": "positive"},
        "质量隐患": {"keywords": ["坏了", "故障", "质量差", "次品", "问题"], "sentiment": "negative"},
        "价格虚高": {"keywords": ["贵", "太贵", "不值", "贵了"], "sentiment": "negative"},
        "体验糟糕": {"keywords": ["难用", "麻烦", "复杂", "不便"], "sentiment": "negative"},
        "虚假宣传": {"keywords": ["虚假", "骗子", "夸大", "不实"], "sentiment": "negative"},
        "售后推诿": {"keywords": ["售后", "推诿", "不管", "踢皮球"], "sentiment": "negative"},
        "安全隐患": {"keywords": ["危险", "安全隐患", "担心", "怕"], "sentiment": "negative"},
    }
    
    def __init__(self):
        self.vector_dim = 128
        self.vectors = []
        self.metadatas = []
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        文本向量化（简化实现：用关键词词频作为向量）
        实际生产环境应使用 sentence-transformers 或 OpenAI embeddings
        """
        vector = np.zeros(self.vector_dim)
        text_lower = text.lower()
        
        keywords_pool = []
        for label, config in self.CLUSTER_LABELS.items():
            keywords_pool.extend(config["keywords"])
        
        for i, keyword in enumerate(keywords_pool[:self.vector_dim]):
            if keyword in text_lower:
                vector[i] = 1.0
        
        text_hash = hash(text_lower)
        np.random.seed(abs(text_hash) % (2**32))
        vector += np.random.randn(self.vector_dim) * 0.1
        
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def add_complaints(self, complaints: List[Dict]) -> int:
        """
        添加抱怨记录到向量库
        complaints: [{"content": str, "source": str, "sentiment": float, ...}]
        返回添加的数量
        """
        for complaint in complaints:
            content = complaint.get("content", "")
            if not content:
                continue
            
            vector = self.embed_text(content)
            self.vectors.append(vector)
            self.metadatas.append({
                "content": content,
                "source": complaint.get("source", "unknown"),
                "complaint_type": complaint.get("complaint_type", "其他"),
                "sentiment": complaint.get("sentiment", 0),
                "cluster": None,
                "added_at": datetime.now().isoformat()
            })
        
        return len(complaints)
    
    def find_similar(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """
        查找与查询文本相似的抱怨
        返回top_k个最相似的抱怨及其相似度
        """
        if not self.vectors:
            return []
        
        query_vector = self.embed_text(query_text)
        
        similarities = []
        for i, vec in enumerate(self.vectors):
            sim = float(np.dot(query_vector, vec))
            similarities.append((i, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, sim in similarities[:top_k]:
            meta = self.metadatas[idx].copy()
            meta["similarity"] = round(sim, 3)
            results.append(meta)
        
        return results
    
    def cluster_complaints(self, n_clusters: int = 8) -> Dict[int, List[Dict]]:
        """
        对所有抱怨进行聚类
        使用简化的K-Means实现（生产环境应用真正的Milvus + FAISS）
        """
        if len(self.vectors) < n_clusters:
            return {}
        
        vectors_array = np.array(self.vectors)
        
        np.random.seed(42)
        initial_indices = np.random.choice(len(vectors_array), n_clusters, replace=False)
        centroids = vectors_array[initial_indices]
        
        for _ in range(20):
            distances = np.linalg.norm(vectors_array[:, np.newaxis] - centroids, axis=2)
            assignments = np.argmin(distances, axis=1)
            
            new_centroids = []
            for k in range(n_clusters):
                mask = assignments == k
                if mask.sum() > 0:
                    new_centroids.append(vectors_array[mask].mean(axis=0))
                else:
                    new_centroids.append(centroids[k])
            
            new_centroids = np.array(new_centroids)
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids
        
        for i, cluster_id in enumerate(assignments):
            self.metadatas[i]["cluster"] = int(cluster_id)
        
        clusters = {}
        for i, cluster_id in enumerate(assignments):
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(self.metadatas[i])
        
        return clusters
    
    def get_cluster_summary(self) -> List[Dict]:
        """
        获取聚类摘要：每个聚类的大小、主要内容、情感倾向
        """
        if not self.metadatas:
            return []
        
        cluster_data = {}
        for meta in self.metadatas:
            cid = meta.get("cluster")
            if cid is None:
                cid = -1
            if cid not in cluster_data:
                cluster_data[cid] = {"count": 0, "sentiments": [], "contents": [], "sources": set()}
            cluster_data[cid]["count"] += 1
            cluster_data[cid]["sentiments"].append(meta.get("sentiment", 0))
            cluster_data[cid]["contents"].append(meta["content"])
            cluster_data[cid]["sources"].add(meta.get("source", "unknown"))
        
        summaries = []
        for cid, data in sorted(cluster_data.items(), key=lambda x: x[1]["count"], reverse=True):
            avg_sentiment = sum(data["sentiments"]) / len(data["sentiments"]) if data["sentiments"] else 0
            
            all_text = " ".join(data["contents"][:10])
            matched_labels = []
            for label, config in self.CLUSTER_LABELS.items():
                count = sum(1 for kw in config["keywords"] if kw in all_text.lower())
                if count > 0:
                    matched_labels.append((label, count))
            matched_labels.sort(key=lambda x: x[1], reverse=True)
            
            summaries.append({
                "cluster_id": int(cid),
                "count": data["count"],
                "percentage": round(data["count"] / len(self.metadatas) * 100, 1),
                "avg_sentiment": round(avg_sentiment, 2),
                "top_sources": list(data["sources"])[:3],
                "theme": matched_labels[0][0] if matched_labels else "未分类",
                "sample_contents": data["contents"][:3]
            })
        
        return summaries
    
    def find_innovation_opportunities(self) -> List[Dict]:
        """
        发现创新机会：高频负面 + 低频正面 = 改进空间大
        逻辑：用户强烈抱怨的点（高频负面），但正面反馈很少提及 = 创新切入点
        """
        if not self.metadatas:
            return []
        
        type_stats = {}
        for meta in self.metadatas:
            ct = meta.get("complaint_type", "其他")
            sentiment = meta.get("sentiment", 0)
            
            if ct not in type_stats:
                type_stats[ct] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
            
            type_stats[ct]["total"] += 1
            if sentiment > 0:
                type_stats[ct]["positive"] += 1
            elif sentiment < 0:
                type_stats[ct]["negative"] += 1
            else:
                type_stats[ct]["neutral"] += 1
        
        opportunities = []
        for ct, stats in type_stats.items():
            if stats["total"] < 5:
                continue
            
            neg_ratio = stats["negative"] / stats["total"]
            pos_ratio = stats["positive"] / stats["total"]
            
            if neg_ratio > 0.3 and pos_ratio < 0.2:
                opportunity_score = int(neg_ratio * 100)
                opportunities.append({
                    "type": ct,
                    "negative_count": stats["negative"],
                    "positive_count": stats["positive"],
                    "opportunity_score": opportunity_score,
                    "reason": f"负面反馈统计{stats['negative']}条，占比{neg_ratio*100:.0f}%，正面反馈仅{pos_ratio*100:.0f}%，存在明显改进空间",
                    "suggestion": f"针对「{ct}」提供差异化解决方案"
                })
        
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return opportunities
    
    def reset(self):
        """清空向量库"""
        self.vectors = []
        self.metadatas = []