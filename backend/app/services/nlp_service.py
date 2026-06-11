from typing import List

import jieba
import jieba.analyse


class NLPService:
    COMPLAINT_TYPES = {
        "性能问题": {"keywords": ["慢", "卡", "耗电", "发热", "崩溃", "闪退", "延迟", "反应慢"], "category": "performance"},
        "功能缺失": {"keywords": ["没有", "缺少", "不能", "无法", "功能", "希望能", "要是能"], "category": "feature"},
        "价格问题": {"keywords": ["贵", "便宜", "性价比", "价格", "太贵", "不值", "划算", "优惠"], "category": "price"},
        "服务体验": {"keywords": ["客服", "服务", "态度", "包装", "物流", "快递", "配送"], "category": "service"},
        "质量缺陷": {"keywords": ["坏", "质量", "劣质", "破损", "故障", "毛病", "差", "烂"], "category": "quality"},
        "安全隐患": {"keywords": ["危险", "安全", "隐患", "泄露", "隐私", "有毒", "伤害"], "category": "safety"},
        "交付问题": {"keywords": ["延迟", "缺货", "拖延", "等待", "发货", "到货", "现货"], "category": "delivery"},
        "其他": {"keywords": [], "category": "other"}
    }

    POSITIVE_WORDS = ["好", "棒", "喜欢", "满意", "推荐", "优秀", "完美", "赞"]
    NEGATIVE_WORDS = ["差", "烂", "垃圾", "失望", "退货", "投诉", "坑", "骗"]

    def __init__(self):
        for word in self.POSITIVE_WORDS + self.NEGATIVE_WORDS:
            jieba.add_word(word)
        for complaint_type in self.COMPLAINT_TYPES.values():
            for keyword in complaint_type["keywords"]:
                jieba.add_word(keyword)

    def tokenize(self, text: str) -> List[str]:
        return list(jieba.cut(text))

    def analyze_sentiment(self, text: str) -> float:
        score = 0.0
        for word in self.POSITIVE_WORDS:
            if word in text:
                score += 1
        for word in self.NEGATIVE_WORDS:
            if word in text:
                score -= 1
        # 检查否定词
        if "不" in text or "没" in text:
            score = -score * 0.5 if score > 0 else score
        return max(-5.0, min(5.0, score))

    def classify_complaint(self, text: str) -> str:
        max_match = 0
        result_type = "其他"

        for complaint_type, config in self.COMPLAINT_TYPES.items():
            if complaint_type == "其他":
                continue
            # 在原文中模糊匹配关键词（包含即可）
            match_count = sum(1 for kw in config["keywords"] if kw in text)
            if match_count > max_match:
                max_match = match_count
                result_type = complaint_type

        return result_type

    def extract_keywords(self, text: str, topk: int = 10) -> List[str]:
        return jieba.analyse.extract_tags(text, topK=topk, withWeight=False)

    def analyze_text(self, text: str) -> dict:
        return {
            "tokens": self.tokenize(text),
            "sentiment": self.analyze_sentiment(text),
            "complaint_type": self.classify_complaint(text),
            "keywords": self.extract_keywords(text)
        }