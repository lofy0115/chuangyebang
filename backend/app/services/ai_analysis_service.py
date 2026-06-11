"""
智能抱怨分析引擎 - 基于关键词+TF-IDF混合聚类的AI抱怨分析
功能：关键词预分类 + 智能聚类发现新模式、痛点发现、情感分析、热度计算
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from collections import Counter
import re
import warnings
warnings.filterwarnings("ignore")

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import normalize


@dataclass
class ComplaintItem:
    id: str
    content: str
    source: str = "unknown"
    likes: int = 0
    comments: int = 0
    shares: int = 0
    timestamp: Optional[str] = None
    embedding: Optional[np.ndarray] = None
    sentiment: float = 0.5
    cluster_id: int = -1
    cluster_label: str = "未分类"
    heat_score: float = 0.0


@dataclass
class PainPoint:
    name: str
    frequency: int
    avg_sentiment: float
    intensity: float
    unmet_score: float
    value_score: float
    sample_complaints: List[str] = field(default_factory=list)


class AIAnalysisService:
    STOPWORDS = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                 '自己', '这', '那', '什么', '怎么', '为什么', '但是', '所以', '就是', '还是',
                 '已经', '一个', '这个', '那个', '能', '还', '可以', '把', '让', '给', '对', '他',
                 '她', '它', '们', '哪', '吗', '呢', '吧', '啊', '哦', '嗯', '呀', '真的', '真是',
                 '太', '非常', '特别', '比较', '相当', '一点', '有点', '还是', '还是说', '虽然'}

    POSITIVE_WORDS = {'好', '棒', '喜欢', '满意', '赞', '优秀', '完美', '支持', '推荐', '开心',
                      '惊喜', '感谢', '信赖', '靠谱', '物超所值', '值得', '舒服', '实用', '方便',
                      '快', '快捷', '迅速', '高效', '干净', '漂亮', '美观', '划算', '优惠', '便宜',
                      '超值', '良心', '负责', '耐心', '热情', '专业', '贴心', '满意', '好评'}
    NEGATIVE_WORDS = {'差', '烂', '垃圾', '失望', '退货', '投诉', '坑', '骗', '坏', '慢', '贵',
                      '难', '烦', '糟糕', '太差', '不值', '后悔', '虚假', '欺骗', '敷衍', '推诿',
                      '不专业', '太差', '无语', '气愤', '恶心', '讨厌', '破损', '失望透顶', '再也不买',
                      '质量差', '服务差', '态度差', '太慢', '等太久', '黑心', '暴利', '套路', '欺诈',
                      '劣质', '粗制滥造', '偷工减料', '甲醛', '致癌', '危险', '隐患', '漏水', '异响'}

    NEGATORS = {'不', '没', '无', '非', '别', '未', '莫', '休', '非', '勿'}

    # 预定义投诉类型关键词
    COMPLAINT_CATEGORIES = {
        "物流配送": ["物流", "快递", "配送", "发货", "送货", "运输", "送货", "到货", "时效", "派送", "仓储", "转运"],
        "商品质量": ["质量", "品质", "坏的", "破损", "瑕疵", "残次", "故障", "损坏", "裂开", "生锈", "异味", "变质"],
        "售后服务": ["售后", "客服", "退换", "维修", "保修", "赔偿", "投诉", "索赔", "投诉", "维权", "处理"],
        "价格问题": ["价格", "贵", "便宜", "性价比", "值不值", "价钱", "收费", "加价", "涨价", "折扣", "降价"],
        "功能体验": ["功能", "效果", "使用", "操作", "体验", "设计", "不合理", "难用", "不方便", "复杂"],
        "虚假宣传": ["虚假", "欺骗", "欺诈", "夸大", "误导", "宣传", "不符", "套路", "货不对板", "图文不符"],
        "食品安全": ["食品", "安全", "卫生", "过期", "变质", "添加剂", "农药", "激素", "致癌", "腹泻", "中毒"],
        "个人信息": ["隐私", "泄露", "信息", "推销", "骚扰", "电话", "短信", "轰炸", "数据"],
        "虚假评价": ["刷单", "刷评", "假评", "水军", "控评", "删评", "黑评", "好评返现"],
    }

    def __init__(self):
        self._vectorizer = None
        self._cluster_id_counter = 0
        jieba.setLogLevel(20)

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            self._vectorizer = TfidfVectorizer(
                analyzer='word',
                max_features=2000,
                min_df=1,
                token_pattern=r'[\u4e00-\u9fa5]+',
            )
        return self._vectorizer

    def _tokenize(self, text: str) -> str:
        words = jieba.cut(text)
        return " ".join([w for w in words if len(w) >= 2 and w not in self.STOPWORDS])

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        tokenized = [self._tokenize(t) for t in texts]
        tfidf_matrix = self.vectorizer.fit_transform(tokenized)
        return tfidf_matrix.toarray()

    def analyze_sentiment(self, text: str) -> float:
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in text)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in text)
        score = (pos_count - neg_count * 1.5) / max(len(text), 10) * 5 + 0.5

        for neg in self.NEGATORS:
            if neg in text:
                idx = text.find(neg)
                rest = text[idx:]
                for pos in self.POSITIVE_WORDS:
                    if pos in rest:
                        score = 1.0 - score
                        break
        return max(0.0, min(1.0, score))

    def _detect_category(self, text: str) -> Optional[str]:
        """用关键词检测投诉类别"""
        best_category = None
        best_score = 0
        for category, keywords in self.COMPLAINT_CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_category = category
        return best_category if best_score > 0 else None

    def _extract_cluster_keywords(self, texts: List[str], top_k: int = 4) -> List[str]:
        """从文本集合提取关键词"""
        word_freq = Counter()
        for text in texts:
            words = jieba.cut(text)
            for w in words:
                if len(w) >= 2 and w not in self.STOPWORDS:
                    word_freq[w] += 1
        return [w for w, _ in word_freq.most_common(top_k)]

    def _build_cluster_label(self, texts: List[str], sentiment_avg: float, cluster_id: int) -> str:
        """构建聚类标签"""
        cat = self._detect_category(texts[0]) if texts else None
        keywords = self._extract_cluster_keywords(texts[:15], top_k=3)
        kw_str = "".join(keywords)

        if cat and kw_str:
            return f"{cat}·{kw_str}"
        elif cat:
            return cat
        elif kw_str:
            sentiment_label = "负面" if sentiment_avg < 0.4 else "中性" if sentiment_avg < 0.6 else "正面"
            return f"{sentiment_label}{kw_str}"
        return "综合抱怨"

    def cluster_complaints(self, items: List[ComplaintItem]) -> None:
        """对抱怨进行聚类：先用类别预分类，再用TF-IDF聚类发现子模式"""
        texts = [item.content for item in items]

        # 预分类：用关键词确定类别
        category_items = {}
        uncategorized = []
        for item in items:
            cat = self._detect_category(item.content)
            if cat:
                if cat not in category_items:
                    category_items[cat] = []
                category_items[cat].append(item)
            else:
                uncategorized.append(item)

        # 对每个类别内部做TF-IDF聚类
        self._cluster_id_counter = 0
        for cat, cat_items in category_items.items():
            if len(cat_items) >= 3:
                # 子聚类
                cat_texts = [it.content for it in cat_items]
                embeddings = self.generate_embeddings(cat_texts)
                norm = normalize(embeddings)

                n_clusters = max(1, min(len(cat_items) // 3, 5))
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    metric='cosine',
                    linkage='average'
                ).fit(norm)

                for i, item in enumerate(cat_items):
                    sub_cluster = clustering.labels_[i]
                    item.cluster_id = self._cluster_id_counter
                    item.cluster_label = f"{cat}-{sub_cluster + 1}"
                    self._cluster_id_counter += 1
            else:
                for item in cat_items:
                    item.cluster_id = self._cluster_id_counter
                    item.cluster_label = cat
                    self._cluster_id_counter += 1

        # 未分类的用整体聚类
        if uncategorized:
            uncategorized_texts = [it.content for it in uncategorized]
            embeddings = self.generate_embeddings(uncategorized_texts)
            if embeddings.shape[1] > 0 and len(uncategorized) >= 2:
                norm = normalize(embeddings)
                n_clusters = max(1, min(len(uncategorized) // 2, 4))
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    metric='cosine',
                    linkage='average'
                ).fit(norm)
                for i, item in enumerate(uncategorized):
                    sub = clustering.labels_[i]
                    keywords = self._extract_cluster_keywords(
                        [it.content for it in uncategorized if
                         (clustering.labels_[list(uncategorized).index(it)] == sub)][:5], top_k=2)
                    kw_str = "".join(keywords)
                    item.cluster_id = self._cluster_id_counter
                    item.cluster_label = kw_str if kw_str else "其他抱怨"
                    if i == 0 or clustering.labels_[i] != clustering.labels_[i-1]:
                        self._cluster_id_counter += 1
            else:
                for item in uncategorized:
                    item.cluster_id = self._cluster_id_counter
                    item.cluster_label = "综合抱怨"
                    self._cluster_id_counter += 1

    def discover_pain_points(self, items: List[ComplaintItem]) -> List[PainPoint]:
        """从聚类结果中发现高价值痛点"""
        cluster_data = {}
        for item in items:
            if item.cluster_id not in cluster_data:
                cluster_data[item.cluster_id] = {
                    "label": item.cluster_label,
                    "texts": [],
                    "sentiments": [],
                    "count": 0,
                    "total_likes": 0,
                    "total_comments": 0
                }
            cluster_data[item.cluster_id]["texts"].append(item.content)
            cluster_data[item.cluster_id]["sentiments"].append(item.sentiment)
            cluster_data[item.cluster_id]["count"] += 1
            cluster_data[item.cluster_id]["total_likes"] += item.likes
            cluster_data[item.cluster_id]["total_comments"] += item.comments

        pain_points = []
        for cid, data in cluster_data.items():
            if data["count"] < 1:
                continue

            avg_sentiment = np.mean(data["sentiments"])
            frequency = data["count"]
            intensity = 1.0 - avg_sentiment

            all_words = " ".join(data["texts"])
            unmet_keywords = ["没有", "缺少", "希望", "应该", "要是", "能否", "想要", "需要",
                             "建议", "能不能", "要是能", "真希望", "要是可以", "多希望能",
                             "怎么不能", "应该要", "强烈建议", "请务必"]
            unmet_count = sum(all_words.count(kw) for kw in unmet_keywords)
            unmet_score = min(1.0, unmet_count / max(frequency, 1) * 0.7)

            engagement = data["total_likes"] * 1.0 + data["total_comments"] * 2.0
            engagement_factor = min(1.0, np.log1p(engagement) / 10)

            value_score = (frequency / 50.0) * 0.25 + intensity * 0.35 + unmet_score * 0.25 + engagement_factor * 0.15
            value_score = min(1.0, value_score)

            pain_points.append(PainPoint(
                name=data["label"],
                frequency=frequency,
                avg_sentiment=avg_sentiment,
                intensity=intensity,
                unmet_score=unmet_score,
                value_score=value_score,
                sample_complaints=data["texts"][:3]
            ))

        pain_points.sort(key=lambda x: x.value_score, reverse=True)
        return pain_points[:10]

    def calculate_heat_score(self, item: ComplaintItem, current_time: datetime) -> float:
        time_weight = 1.0
        if item.timestamp:
            try:
                dt = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
                days_ago = (current_time - dt.replace(tzinfo=None)).days
                time_weight = np.exp(-days_ago / 30)
            except Exception:
                pass

        engagement = item.likes * 1.0 + item.comments * 2.0 + item.shares * 3.0
        engagement_weight = np.log1p(engagement) / 10
        sentiment_factor = 1.0 - item.sentiment

        score = (time_weight * 0.2 + engagement_weight * 0.3 + sentiment_factor * 0.5) * 100
        return round(min(100, score), 2)

    def _generate_insight(self, pp: PainPoint, all_items: List[ComplaintItem]) -> Dict:
        priority = "紧急" if pp.intensity > 0.7 else "中等" if pp.intensity > 0.5 else "一般"

        # 生成具体建议
        if "物流" in pp.name or "配送" in pp.name:
            suggestion = "优化物流配送体系，选择更可靠的物流合作伙伴，设置预期时效提醒"
        elif "质量" in pp.name or "品质" in pp.name:
            suggestion = "严格品控流程，增加产品检验环节，建立质量追溯体系"
        elif "服务" in pp.name or "售后" in pp.name:
            suggestion = "建立专业客服团队，优化投诉处理流程，设置SLA响应时限"
        elif "价格" in pp.name or "性价比" in pp.name:
            suggestion = "优化成本结构或调整定价策略，突出产品核心价值增加溢价能力"
        elif "功能" in pp.name or "体验" in pp.name:
            suggestion = "收集用户反馈，优先改进高呼声功能，简化操作流程"
        elif "虚假" in pp.name or "欺骗" in pp.name:
            suggestion = "立即核查宣传内容，确保与实际产品一致，建立诚信经营体系"
        elif "安全" in pp.name:
            suggestion = "排查安全隐患，必要时启动召回，公开说明安全改进措施"
        elif pp.unmet_score > 0.4:
            suggestion = f"用户存在未满足需求（未满足指数:{pp.unmet_score:.0%}），建议做专项用户调研确认需求真伪和市场规模"
        else:
            suggestion = f"该痛点出现{pp.frequency}次，建议分析根因后制定改进计划"

        return {
            "type": "pain_point",
            "name": pp.name,
            "description": f"出现{pp.frequency}次，情感强度{pp.intensity:.0%}，未满足需求指数{pp.unmet_score:.0%}",
            "frequency": pp.frequency,
            "sentiment": round(pp.avg_sentiment, 3),
            "intensity": round(pp.intensity, 3),
            "unmet_score": round(pp.unmet_score, 3),
            "value_score": round(pp.value_score, 3),
            "priority": priority,
            "suggestion": suggestion,
            "samples": pp.sample_complaints[:2]
        }

    def analyze_complaints(self, complaints: List[dict]) -> dict:
        """主分析接口"""
        if not complaints:
            return {"classified": [], "pain_points": [], "insights": [], "statistics": {}}

        items = []
        for i, c in enumerate(complaints):
            item = ComplaintItem(
                id=str(c.get("id", i)),
                content=c.get("content", ""),
                source=c.get("source", "unknown"),
                likes=c.get("likes", 0),
                comments=c.get("comments", 0),
                shares=c.get("shares", 0),
                timestamp=c.get("timestamp")
            )
            item.sentiment = self.analyze_sentiment(item.content)
            items.append(item)

        self.cluster_complaints(items)

        pain_points = self.discover_pain_points(items)

        current_time = datetime.now()
        classified = []
        for item in items:
            item.heat_score = self.calculate_heat_score(item, current_time)
            sentiment_label = "负面" if item.sentiment < 0.4 else "中性" if item.sentiment < 0.6 else "正面"
            classified.append({
                "id": item.id,
                "content": item.content,
                "source": item.source,
                "likes": item.likes,
                "comments": item.comments,
                "sentiment": round(item.sentiment, 3),
                "sentiment_label": sentiment_label,
                "cluster_id": item.cluster_id,
                "cluster_label": item.cluster_label,
                "heat_score": item.heat_score
            })

        insights = [self._generate_insight(pp, items) for pp in pain_points[:5]]

        sentiment_scores = [c.sentiment for c in items]
        pos = sum(1 for s in sentiment_scores if s >= 0.6)
        neu = sum(1 for s in sentiment_scores if 0.4 <= s < 0.6)
        neg = sum(1 for s in sentiment_scores if s < 0.4)

        statistics = {
            "total": len(items),
            "clusters": len(set(item.cluster_id for item in items)),
            "avg_sentiment": round(np.mean(sentiment_scores), 3),
            "sentiment_distribution": {"positive": pos, "neutral": neu, "negative": neg},
            "avg_heat_score": round(np.mean([c.heat_score for c in items]), 2),
            "top_pain_points": [{"name": pp.name, "value_score": round(pp.value_score, 3),
                                 "priority": "紧急" if pp.intensity > 0.7 else "中等" if pp.intensity > 0.5 else "一般"}
                                for pp in pain_points[:3]],
            "unmet_needs_count": sum(1 for pp in pain_points if pp.unmet_score > 0.3),
            "categories": list(set(item.cluster_label.split("-")[0] for item in items if "-" in item.cluster_label))
        }

        return {
            "classified": classified,
            "pain_points": [{"name": pp.name, "frequency": pp.frequency,
                             "avg_sentiment": round(pp.avg_sentiment, 3),
                             "intensity": round(pp.intensity, 3),
                             "unmet_score": round(pp.unmet_score, 3),
                             "value_score": round(pp.value_score, 3),
                             "samples": pp.sample_complaints}
                            for pp in pain_points],
            "insights": insights,
            "statistics": statistics
        }