from typing import List, Optional

from .nlp_service import NLPService


class AnalysisService:
    INDUSTRIES = {
        "母婴": ["奶粉", "纸尿裤", "婴儿车", "奶瓶", "辅食"],
        "美妆": ["护肤品", "化妆品", "口红", "面膜", "精华"],
        "智能家居": ["扫地机器人", "智能音箱", "智能门锁", "空气净化器"],
        "新能源汽车": ["电动车", "充电桩", "电池", "续航"],
        "食品": ["零食", "饮料", "保健品", "有机食品"]
    }

    CUSTOMER_SEGMENTS = {
        "价格敏感型": ["便宜", "优惠", "性价比", "打折"],
        "品质优先型": ["质量", "高端", "品牌", "正宗"],
        "尝鲜体验型": ["新品", "爆款", "网红", "限量"],
        "实用主义型": ["实用", "耐用", "性价比", "够用"]
    }

    def __init__(self):
        self.nlp_service = NLPService()

    def search_industry(self, keyword: str) -> Optional[dict]:
        # 先精确匹配行业名
        if keyword in self.INDUSTRIES:
            return {"industry": keyword, "matched_keyword": keyword}
        # 再匹配关键词
        for industry, keywords in self.INDUSTRIES.items():
            for kw in keywords:
                if kw in keyword or keyword in kw:
                    return {"industry": industry, "matched_keyword": kw}
        return None

    def get_complaint_types(self) -> List[dict]:
        return [
            {"name": key, "category": value["category"]}
            for key, value in NLPService.COMPLAINT_TYPES.items()
        ]

    def generate_mock_data(self, keyword: str, count: int = 100) -> List[dict]:
        industry_info = self.search_industry(keyword)
        industry = industry_info["industry"] if industry_info else "通用"

        templates = [
            "收到货了，质量很好，满意",
            "物流有点慢，等了好几天",
            "性价比不错，会回购",
            "包装太差了，到手都破损了",
            "客服态度差，问题没解决",
            "便宜是便宜，就是质量一般",
            "新品尝鲜，感觉还不错",
            "跟风买的，没有宣传的那么好",
        ]

        data = []
        for i in range(count):
            text = templates[i % len(templates)]
            analysis = self.nlp_service.analyze_text(text)
            data.append({
                "id": i + 1,
                "text": text,
                "industry": industry,
                "sentiment": analysis["sentiment"],
                "complaint_type": analysis["complaint_type"]
            })
        return data

    def analyze_industry(self, keyword: str) -> Optional[dict]:
        industry_info = self.search_industry(keyword)
        if not industry_info:
            return None

        mock_data = self.generate_mock_data(keyword, count=50)

        sentiment_scores = [item["sentiment"] for item in mock_data]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        complaint_counts = {}
        for item in mock_data:
            ct = item["complaint_type"]
            complaint_counts[ct] = complaint_counts.get(ct, 0) + 1

        # 构建符合AnalyzeResponse的数据结构
        total = len(mock_data)
        complaint_distribution = [
            {"type": ct, "count": count, "percentage": round(count / total * 100, 1)}
            for ct, count in complaint_counts.items()
        ]

        return {
            "industry": industry_info["industry"],
            "total_records": total,
            "complaint_distribution": complaint_distribution,
            "top_value_needs": [
                {"need": "高品质", "priority": 85},
                {"need": "高性价比", "priority": 72},
                {"need": "便捷服务", "priority": 65}
            ],
            "customer_segments": [
                {"segment": "价格敏感型", "needs": ["便宜", "优惠", "划算"]},
                {"segment": "品质优先型", "needs": ["质量", "高端", "品牌"]}
            ]
        }