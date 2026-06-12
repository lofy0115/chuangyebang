import random
from typing import List, Optional

from .nlp_service import NLPService


class AnalysisService:
    """行业分析服务 - 支持任意关键词作为行业名"""

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

    # 按行业定制的评论模板库（关键改进：不同行业有不同抱怨）
    INDUSTRY_TEMPLATES = {
        "母婴": [
            ("质量很好，会回购", "positive", "其他"),
            ("价格太贵了，涨了好几次价", "negative", "价格问题"),
            ("用了几天就坏了，质量太差", "negative", "质量缺陷"),
            ("物流超慢，等了十天才到", "negative", "交付问题"),
            ("成分不安全，不敢给孩子用", "negative", "安全隐患"),
            ("包装破损，东西洒了一地", "negative", "服务体验"),
            ("功能太少，没有我想买的型号", "negative", "功能缺失"),
            ("非常好用，宝宝喜欢", "positive", "其他"),
        ],
        "民宿": [
            ("房间和照片差距太大，欺骗消费者", "negative", "质量缺陷"),
            ("位置偏远，交通不便", "negative", "服务体验"),
            ("价格周末翻倍，太坑了", "negative", "价格问题"),
            ("卫生太差，床单有污渍", "negative", "质量缺陷"),
            ("入住体验很棒，下次还来", "positive", "其他"),
            ("隔音太差，晚上睡不着", "negative", "性能问题"),
            ("没有空调，夏天热死了", "negative", "功能缺失"),
            ("房东态度差，沟通困难", "negative", "服务体验"),
            ("设施老旧，很多东西坏了", "negative", "质量缺陷"),
            ("性价比高，适合穷游", "positive", "价格问题"),
        ],
        "咖啡": [
            ("口感香醇，回味无穷", "positive", "其他"),
            ("价格太贵，一杯30多", "negative", "价格问题"),
            ("出餐太慢，等了20分钟", "negative", "性能问题"),
            ("环境嘈杂，无法办公", "negative", "服务体验"),
            ("豆子新鲜，品质稳定", "positive", "其他"),
            ("性价比高，常来", "positive", "价格问题"),
            ("机器经常故障，多次退款", "negative", "性能问题"),
            ("店员不专业，点单常出错", "negative", "服务体验"),
            ("新品好喝，推荐", "positive", "其他"),
            ("外卖洒了，包装太差", "negative", "服务体验"),
        ],
        "新能源汽车": [
            ("续航虚标严重，官方数据不准", "negative", "性能问题"),
            ("充电桩太少，排队太久", "negative", "功能缺失"),
            ("售后服务推诿，问题不给解决", "negative", "服务体验"),
            ("智能系统经常死机，不稳定", "negative", "性能问题"),
            ("性价比超高，配置良心", "positive", "价格问题"),
            ("驾驶体验很好，动力充沛", "positive", "其他"),
            ("质量可靠，安全配置丰富", "positive", "其他"),
            ("充电太慢，浪费时间", "negative", "性能问题"),
            ("价格不稳定，买完就降价", "negative", "价格问题"),
            ("辅助驾驶功能鸡肋，不好用", "negative", "功能缺失"),
        ],
        "健身房": [
            ("器械老旧，很多坏了没人修", "negative", "质量缺陷"),
            ("教练专业，指导到位", "positive", "其他"),
            ("价格虚高，性价比低", "negative", "价格问题"),
            ("环境差，通风不好有异味", "negative", "服务体验"),
            ("课程丰富，选择多样", "positive", "其他"),
            ("推销严重，服务态度差", "negative", "服务体验"),
            ("搬家后用不了，不方便", "negative", "功能缺失"),
            ("24小时营业，随时能去", "positive", "其他"),
            ("会员权益难兑现，虚假宣传", "negative", "服务体验"),
            ("隐私性差，人太多太挤", "negative", "服务体验"),
        ],
    }

    # 通用意大利面模板（当行业不在预设里时使用）
    DEFAULT_TEMPLATES = [
        ("质量很好，满足预期", "positive", "其他"),
        ("价格偏贵，性价比一般", "negative", "价格问题"),
        ("服务不错，体验舒适", "positive", "服务体验"),
        ("功能基本够用，没有明显缺陷", "neutral", "功能缺失"),
        ("物流及时，包装完好", "positive", "交付问题"),
        ("性能稳定，使用顺畅", "positive", "性能问题"),
        ("客服态度好，问题解决快", "positive", "服务体验"),
        ("设计合理，美观实用", "positive", "其他"),
        ("价格实惠，值得购买", "positive", "价格问题"),
        ("质量一般，有待改进", "negative", "质量缺陷"),
        ("发货快，效率高", "positive", "交付问题"),
        ("操作简单，上手容易", "positive", "功能缺失"),
        ("有点小问题，但不影响使用", "negative", "质量缺陷"),
        ("与描述基本一致", "neutral", "其他"),
        ("性价比高，推荐购买", "positive", "价格问题"),
    ]

    def __init__(self):
        self.nlp_service = NLPService()

    def search_industry(self, keyword: str) -> Optional[dict]:
        """对任意关键词都返回结果，把关键词作为行业名"""
        # 先精确匹配已知行业名
        if keyword in self.INDUSTRIES:
            return {"industry": keyword, "matched_keyword": keyword}
        # 再通过关键词匹配
        for industry, keywords in self.INDUSTRIES.items():
            for kw in keywords:
                if kw in keyword or keyword in kw:
                    return {"industry": industry, "matched_keyword": kw}
        # 关键修复：对任意未知关键词，直接用关键词作为行业名
        return {"industry": keyword, "matched_keyword": keyword}

    def get_complaint_types(self) -> List[dict]:
        return [
            {"name": key, "category": value["category"]}
            for key, value in NLPService.COMPLAINT_TYPES.items()
        ]

    def generate_mock_data(self, keyword: str, count: int = 50) -> List[dict]:
        """根据关键词动态生成相关评论数据"""
        industry_info = self.search_industry(keyword)
        industry = industry_info["industry"]

        # 优先用行业专属模板，否则用通用模板
        templates = self.INDUSTRY_TEMPLATES.get(industry, self.DEFAULT_TEMPLATES)

        data = []
        for i in range(count):
            # 每次随机选择模板，引入变化
            text, sentiment_label, complaint_type = random.choice(templates)
            # 添加随机变化：换词、添加细节
            text = self._vary_text(text, industry)
            sentiment = self.nlp_service.analyze_sentiment(text)
            if sentiment == 0:
                sentiment = 1.0 if sentiment_label == "positive" else -1.0
            data.append({
                "id": i + 1,
                "text": text,
                "industry": industry,
                "sentiment": sentiment,
                "complaint_type": complaint_type
            })
        return data

    def _vary_text(self, base_text: str, industry: str) -> str:
        """对基础评论文本进行随机变化，模拟真实多样性"""
        variations = [
            "",
            "总体来说 ",
            "用了几天感觉 ",
            "朋友推荐的，确实 ",
            "性价比一般，但 ",
            "虽然有点小贵，不过 ",
            "实际体验下来 ",
        ]
        prefix = random.choice(variations)
        suffixes = [
            "，给个好评",
            "，中规中矩",
            "，有待观察",
            "，值得关注",
            "，希望改进",
            "，推荐给朋友",
            "",
        ]
        suffix = random.choice(suffixes)
        return f"{prefix}{base_text}{suffix}"

    def analyze_industry(self, keyword: str) -> dict:
        """核心分析：对任意关键词进行分析"""
        industry_info = self.search_industry(keyword)
        industry = industry_info["industry"]

        mock_data = self.generate_mock_data(keyword, count=50)

        sentiment_scores = [item["sentiment"] for item in mock_data]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        # 统计抱怨分布
        complaint_counts = {}
        for item in mock_data:
            ct = item["complaint_type"]
            complaint_counts[ct] = complaint_counts.get(ct, 0) + 1

        total = len(mock_data)
        complaint_distribution = [
            {"type": ct, "count": count, "percentage": round(count / total * 100, 1)}
            for ct, count in sorted(complaint_counts.items(), key=lambda x: -x[1])
        ]

        # 根据实际抱怨分布生成高价值痛点（关键改进）
        top_pain_points = self._extract_pain_points(complaint_counts, industry)

        # 根据行业生成客户细分
        segments = self._generate_customer_segments(industry, complaint_counts)

        return {
            "industry": industry,
            "total_records": total,
            "avg_sentiment": round(avg_sentiment, 2),
            "complaint_distribution": complaint_distribution,
            "top_value_needs": top_pain_points,
            "customer_segments": segments,
            "sample_data": mock_data[:5]
        }

    def _extract_pain_points(self, complaint_counts: dict, industry: str) -> List[dict]:
        """根据抱怨分布提取高价值痛点"""
        pain_point_map = {
            "性能问题": [
                {"need": "流畅稳定的使用体验", "pain": "卡顿、延迟影响效率", "priority": 90},
                {"need": "省电低耗", "pain": "耗电太快是核心痛点", "priority": 85},
            ],
            "价格问题": [
                {"need": "合理定价，性价比高", "pain": "价格超出心理预期", "priority": 88},
                {"need": "透明收费，无隐藏费用", "pain": "价格不透明让人不信任", "priority": 80},
            ],
            "功能缺失": [
                {"need": "核心功能完善好用", "pain": "想要的功能没有", "priority": 85},
                {"need": "个性化定制能力", "pain": "无法满足个性化需求", "priority": 70},
            ],
            "服务体验": [
                {"need": "专业及时的客服支持", "pain": "问题得不到及时解决", "priority": 82},
                {"need": "省心省力的全流程体验", "pain": "流程复杂让人疲惫", "priority": 75},
            ],
            "质量缺陷": [
                {"need": "质量可靠，经久耐用", "pain": "质量差导致频繁维修或更换", "priority": 92},
                {"need": "安全无隐患", "pain": "安全隐患让人担忧", "priority": 88},
            ],
            "安全隐患": [
                {"need": "安全有保障", "pain": "安全隐患让人不敢购买", "priority": 95},
                {"need": "隐私数据保护", "pain": "隐私泄露风险", "priority": 87},
            ],
            "交付问题": [
                {"need": "及时可靠的交付", "pain": "延迟交货影响计划", "priority": 80},
                {"need": "现货供应，无需等待", "pain": "缺货需要等待", "priority": 75},
            ],
            "其他": [
                {"need": "整体满意，用得放心", "pain": "整体体验有待提升", "priority": 60},
            ],
        }

        result = []
        for ct, count in sorted(complaint_counts.items(), key=lambda x: -x[1]):
            if ct in pain_point_map:
                for p in pain_point_map[ct]:
                    p["source_complaints"] = count
                    result.append(p)
                    if len(result) >= 5:
                        return result
        return result[:5]

    def _generate_customer_segments(self, industry: str, complaint_counts: dict) -> List[dict]:
        """根据行业和抱怨分布生成客户画像"""
        # 根据主要抱怨类型推断客户特征
        primary_complaints = sorted(complaint_counts.items(), key=lambda x: -x[1])[:3]
        primary_types = [ct for ct, _ in primary_complaints]

        segments = []

        if "价格问题" in primary_types:
            segments.append({
                "segment": "价格敏感型",
                "needs": ["实惠", "性价比", "优惠活动", "比质比价"],
                "pain_points": ["价格高", "不值这个价"]
            })
        if "质量缺陷" in primary_types or "安全隐患" in primary_types:
            segments.append({
                "segment": "品质优先型",
                "needs": ["质量可靠", "安全放心", "经久耐用"],
                "pain_points": ["质量差", "存在安全隐患"]
            })
        if "性能问题" in primary_types:
            segments.append({
                "segment": "体验导向型",
                "needs": ["流畅体验", "操作简便", "性能强劲"],
                "pain_points": ["卡顿", "反应慢", "操作复杂"]
            })
        if "服务体验" in primary_types:
            segments.append({
                "segment": "服务敏感型",
                "needs": ["贴心服务", "售后保障", "及时响应"],
                "pain_points": ["服务态度差", "问题解决慢"]
            })

        if not segments:
            segments.append({
                "segment": "综合型消费者",
                "needs": ["质量", "价格", "服务均衡"],
                "pain_points": ["整体体验待提升"]
            })

        return segments