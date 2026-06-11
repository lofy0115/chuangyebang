from typing import Any, Dict, List, Optional
import math


class MonetizationService:
    """商业化服务（利润模式设计），提供7种利润模式模板及相关分析功能"""

    PROFIT_MODELS = {
        "product_sales": {
            "name": "产品销售",
            "description": "直接销售实体或数字产品获取利润",
            "applicable_industries": ["制造业", "零售", "电商", "软件"],
            "key_metrics": ["单价", "销量", "毛利率", "库存周转率"],
            "revenue_formula": "收入 = 单价 × 销量",
            "cost_factors": ["生产成本", "运输成本", "营销成本", "渠道分成"]
        },
        "subscription": {
            "name": "订阅制",
            "description": "周期性收取订阅费获取持续收入",
            "applicable_industries": ["SaaS", "媒体", "教育", "会员服务"],
            "key_metrics": ["月/年费", "订阅人数", "流失率", "LTV"],
            "revenue_formula": "月收入 = 月费 × 订阅人数",
            "cost_factors": ["客户服务成本", "内容成本", "服务器成本", "营销成本"]
        },
        "freemium": {
            "name": "免费增值",
            "description": "基础功能免费，高级功能收费",
            "applicable_industries": ["SaaS", "游戏", "工具软件", "流媒体"],
            "key_metrics": ["免费用户数", "付费转化率", "ARPPU", "获客成本"],
            "revenue_formula": "月收入 = 免费用户数 × 转化率 × ARPPU",
            "cost_factors": ["服务器成本", "免费功能成本", "营销成本", "支付通道费"]
        },
        "platform_commission": {
            "name": "平台抽佣",
            "description": "搭建交易平台并从交易中抽取佣金",
            "applicable_industries": ["电商平台", "共享经济", "招聘平台", "外卖平台"],
            "key_metrics": ["GMV", "抽佣比例", "活跃卖家数", "活跃买家数"],
            "revenue_formula": "收入 = GMV × 抽佣比例",
            "cost_factors": ["平台维护成本", "支付处理费", "客服成本", "推广补贴"]
        },
        "data_service": {
            "name": "数据服务",
            "description": "收集、分析、销售数据或数据洞察",
            "applicable_industries": ["金融", "医疗", "营销", "政府服务"],
            "key_metrics": ["数据条目数", "客户数", "单价", "数据准确率"],
            "revenue_formula": "收入 = 客户数 × 客单价",
            "cost_factors": ["数据采集成本", "存储成本", "分析成本", "合规成本"]
        },
        "tech_licensing": {
            "name": "技术授权",
            "description": "将技术、专利或品牌授权给他人使用",
            "applicable_industries": ["专利技术", "品牌授权", "franchise", "内容IP"],
            "key_metrics": ["授权费", "版权费", "授权数量", "许可期限"],
            "revenue_formula": "收入 = 授权费 + 版权费 × 销售量",
            "cost_factors": ["研发成本", "法务成本", "维护成本", "维权成本"]
        },
        "advertising": {
            "name": "广告变现",
            "description": "通过广告展示或点击获取收入",
            "applicable_industries": ["媒体", "社交", "搜索", "内容平台"],
            "key_metrics": ["DAU/MAU", "广告展示量", "点击率", "CPM/CPC"],
            "revenue_formula": "收入 = 广告展示量 × CPM / 1000",
            "cost_factors": ["流量获取成本", "服务器成本", "广告代理费", "用户体验损耗"]
        }
    }

    def get_profit_model_templates(self) -> Dict[str, Any]:
        """获取所有利润模式模板"""
        return self.PROFIT_MODELS

    def get_single_model_template(self, model_key: str) -> Optional[Dict[str, Any]]:
        """获取单个利润模式模板"""
        return self.PROFIT_MODELS.get(model_key)

    def recommend_model(self, analysis_result: dict) -> List[Dict[str, Any]]:
        """基于分析结果推荐适合的利润模式"""
        industry = analysis_result.get("industry", "")
        total_records = analysis_result.get("total_records", 0)
        complaint_dist = analysis_result.get("complaint_distribution", [])
        customer_segments = analysis_result.get("customer_segments", [])
        top_value_needs = analysis_result.get("top_value_needs", [])

        scores = {}
        for key, model in self.PROFIT_MODELS.items():
            score = 0
            reasons = []

            # 基于记录数量判断市场成熟度
            if total_records > 100:
                if key == "data_service":
                    score += 25
                    reasons.append("市场数据丰富，适合数据洞察服务")
                elif key == "advertising":
                    score += 20
                    reasons.append("用户基数大，广告变现潜力强")
            elif total_records > 30:
                if key == "product_sales":
                    score += 20
                    reasons.append("市场存在明确产品需求")
                elif key == "subscription":
                    score += 15
                    reasons.append("用户有持续服务需求")

            # 基于抱怨分布判断痛点类型
            if complaint_dist:
                top_complaints = [c["type"] for c in sorted(complaint_dist, key=lambda x: x["count"], reverse=True)[:2]]

                if "价格问题" in top_complaints:
                    if key == "freemium":
                        score += 30
                        reasons.append("用户对价格敏感，免费模式降低门槛")
                    elif key == "platform_commission":
                        score += 15
                        reasons.append("平台比价功能满足价格敏感用户")

                if "服务体验" in top_complaints:
                    if key == "subscription":
                        score += 30
                        reasons.append("用户愿意为优质服务付费")
                    elif key == "data_service":
                        score += 20
                        reasons.append("数据驱动的服务可提升体验")

                if "质量缺陷" in top_complaints or "安全隐患" in top_complaints:
                    if key == "product_sales":
                        score += 25
                        reasons.append("高品质产品可解决质量痛点")
                    elif key == "tech_licensing":
                        score += 20
                        reasons.append("授权成熟技术可保障质量")

                if "功能缺失" in top_complaints:
                    if key == "freemium":
                        score += 20
                        reasons.append("基础免费+高级付费满足不同需求")
                    elif key == "subscription":
                        score += 15
                        reasons.append("持续迭代功能满足用户期望")

            # 基于客户细分
            for seg in customer_segments:
                seg_name = seg.get("segment", "")
                if "价格敏感" in seg_name:
                    if key in ["freemium", "platform_commission"]:
                        score += 15
                        reasons.append("满足价格敏感型用户")
                elif "品质" in seg_name or "高端" in seg_name:
                    if key in ["product_sales", "subscription"]:
                        score += 15
                        reasons.append("满足品质优先型用户")

            # 基于价值需求
            for need in top_value_needs:
                need_text = need.get("need", "")
                if "高性价比" in need_text:
                    if key == "freemium":
                        score += 15
                elif "高品质" in need_text or "高端" in need_text:
                    if key in ["product_sales", "subscription"]:
                        score += 15

            # 数据服务适合创业帮
            if key == "data_service":
                score += 20
                reasons.append("消费者洞察服务是创业帮核心价值")

            scores[key] = {
                "model_key": key,
                "model_name": model["name"],
                "description": model["description"],
                "match_score": min(score, 100),
                "reason": "；".join(reasons) if reasons else self._generate_recommend_reason(key, analysis_result)
            }

        sorted_recommendations = sorted(scores.values(), key=lambda x: x["match_score"], reverse=True)
        return sorted_recommendations[:5]

    def _generate_recommend_reason(self, model_key: str, analysis_result: dict) -> str:
        industry = analysis_result.get("industry", "")
        reasons = {
            "product_sales": f"适合{industry}行业的产品直接销售模式",
            "subscription": f"{industry}行业用户对付费内容有持续需求",
            "freemium": f"通过免费引流+付费转化的方式快速获客",
            "platform_commission": "平台撮合交易可实现多方共赢",
            "data_service": "基于行业数据提供增值服务",
            "tech_licensing": "技术授权可快速实现规模化",
            "advertising": "规模化用户后可实现广告变现"
        }
        return reasons.get(model_key, "综合评估后的推荐选择")

    def calculate_unit_economics(self, model_key: str, params: dict) -> Dict[str, Any]:
        """计算单位经济模型"""
        model = self.PROFIT_MODELS.get(model_key, {})
        margin = params.get("margin", 0.5)
        price = params.get("avg_price", 100)
        customers = params.get("customer_count", 1000)
        retention = params.get("retention_rate", 0.8)
        cac = params.get("cac", 300)

        mrr = price * customers * retention
        arr = mrr * 12

        if retention > 0 and retention < 1:
            avg_lifetime = 1 / (1 - retention)
        else:
            avg_lifetime = 1
        ltv = price * retention / (1 - retention) if retention < 1 else price

        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        gross_profit = arr * margin
        breakeven = int(cac / (price * margin)) if margin > 0 else 0

        health = "优秀" if ltv_cac_ratio > 3 and retention > 0.8 else \
                 "良好" if ltv_cac_ratio > 1 and retention > 0.7 else \
                 "一般" if ltv_cac_ratio > 1 else "警告"

        return {
            "model_key": model_key,
            "model_name": model.get("name", model_key),
            "mrr": round(mrr, 2),
            "arr": round(arr, 2),
            "ltv": round(ltv, 2),
            "cac": cac,
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "gross_profit": round(gross_profit, 2),
            "breakeven_customers": breakeven,
            "health_check": health
        }

    def forecast_revenue(self, model_key: str, params: dict, months: int = 12) -> Dict[str, Any]:
        """收入预测"""
        model = self.PROFIT_MODELS.get(model_key, {})
        base_customers = params.get("customer_count", 100)
        price = params.get("avg_price", 99)
        retention = params.get("retention_rate", 0.8)
        growth_rate = params.get("growth_rate", 0.1)
        margin = params.get("margin", 0.5)

        projections = []
        current_customers = base_customers

        for month in range(1, months + 1):
            revenue = current_customers * price
            cost = revenue / margin if margin > 0 else revenue
            projections.append({
                "month": month,
                "customers": current_customers,
                "revenue": round(revenue, 2),
                "gross_profit": round(revenue * margin, 2)
            })
            current_customers = int(current_customers * (1 + growth_rate))
            growth_rate = max(0.02, growth_rate * 0.95)

        total_revenue = sum(p["revenue"] for p in projections)
        total_profit = sum(p["gross_profit"] for p in projections)

        return {
            "model_name": model.get("name", model_key),
            "projection": projections,
            "total_revenue_12m": round(total_revenue, 2),
            "total_profit_12m": round(total_profit, 2)
        }

    def compare_models(self, model_params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对比多个利润模式"""
        results = []
        for mp in model_params:
            model_key = mp.get("model_key", "")
            params = mp.get("params", {})
            result = self.calculate_unit_economics(model_key, params)
            result["model_key"] = model_key
            results.append(result)

        return sorted(results, key=lambda x: x["ltv_cac_ratio"], reverse=True)
