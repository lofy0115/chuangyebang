from typing import Any, List


class BusinessModelService:
    """商业模式设计服务，整合《精益创业》和《商业模式新生代》方法论"""

    def generate_lean_canvas(self, analysis_result: dict) -> dict:
        """生成精益画布（Lean Canvas）"""
        industry = analysis_result.get("industry", "通用行业")
        complaint_dist = analysis_result.get("complaint_distribution", [])
        customer_segments = analysis_result.get("customer_segments", [])

        # 从抱怨分布中提取Top3痛点作为问题
        top_problems = []
        if isinstance(complaint_dist, list):
            sorted_problems = sorted(complaint_dist, key=lambda x: x.get("count", 0), reverse=True)[:3]
            top_problems = [{"rank": i+1, "title": p.get("type", ""), "percentage": p.get("percentage", 0)} for i, p in enumerate(sorted_problems)]
        elif isinstance(complaint_dist, dict):
            sorted_items = sorted(complaint_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            top_problems = [{"rank": i+1, "title": ct, "percentage": pct} for i, (ct, pct) in enumerate(sorted_items)]

        # 自动生成解决方案建议
        solutions = [
            {"title": f"解决{top_problems[0]['title']}" if top_problems else "优化核心功能"},
            {"title": "提升用户体验"},
            {"title": "差异化竞争"}
        ]

        return {
            "problem": top_problems,
            "solution": solutions,
            "unique_value_proposition": f"为{industry}用户提供更好的解决方案",
            "unfair_advantage": ["专利技术", "独家资源", "先发优势"],
            "key_metrics": ["用户留存率", "日活跃用户", "转化率"],
            "channels": ["线上渠道", "社交媒体", "口碑传播"],
            "cost_structure": "固定成本 + 变动成本",
            "revenue_streams": ["产品销售", "增值服务", "订阅收费"]
        }

    def generate_business_model_canvas(self, analysis_result: dict) -> dict:
        """生成商业模式画布（Business Model Canvas）"""
        industry = analysis_result.get("industry", "通用行业")
        customer_segments = analysis_result.get("customer_segments", [])

        return {
            "customer_segments": [seg.get("segment", "") for seg in customer_segments] if customer_segments else ["目标客户群"],
            "value_propositions": ["差异化价值", "高品质", "高性价比"],
            "channels": ["线上直销", "渠道分销", "社交媒体"],
            "customer_relationships": ["自助服务", "社区互动", "专属客服"],
            "revenue_streams": ["产品销售", "订阅收费", "广告收入"],
            "key_resources": ["技术团队", "知识产权", "供应链"],
            "key_activities": ["产品研发", "市场营销", "客户服务"],
            "key_partners": ["供应商", "渠道商", "战略合作伙伴"],
            "cost_structure": "研发成本 + 营销成本 + 运营成本"
        }

    def generate_value_proposition_canvas(self, analysis_result: dict) -> dict:
        """生成价值主张画布（Value Proposition Canvas）"""
        industry = analysis_result.get("industry", "通用行业")
        customer_segments = analysis_result.get("customer_segments", [])

        return {
            "customer_jobs": ["寻找合适的产品", "解决实际问题", "获得性价比"],
            "pains": ["价格高", "质量不稳定", "服务差"],
            "gains": ["高品质", "良好体验", "社会认可"],
            "products_services": ["核心产品", "增值服务", "解决方案"],
            "gain_creators": ["提升品质", "优化体验", "增加便利"],
            "pain_relievers": ["降低价格", "保证质量", "提升服务"]
        }

    def auto_fill_from_analysis(self, analysis_result: dict) -> dict:
        """基于分析结果自动填充所有画布"""
        lean_canvas = self.generate_lean_canvas(analysis_result)
        business_model_canvas = self.generate_business_model_canvas(analysis_result)
        value_proposition_canvas = self.generate_value_proposition_canvas(analysis_result)
        return {
            "lean_canvas": lean_canvas,
            "business_model_canvas": business_model_canvas,
            "value_proposition_canvas": value_proposition_canvas,
        }

    def calculate_model_score(self, model: dict) -> float:
        """计算画布完整性得分（0-100）"""
        total_fields = 0
        filled_fields = 0

        for section_key, section_value in model.items():
            if isinstance(section_value, dict):
                for value in section_value.values():
                    total_fields += 1
                    if self._is_field_filled(value):
                        filled_fields += 1
            elif isinstance(section_value, list):
                total_fields += 1
                if self._is_field_filled(section_value):
                    filled_fields += 1
            elif isinstance(section_value, str):
                total_fields += 1
                if self._is_field_filled(section_value):
                    filled_fields += 1

        if total_fields == 0:
            return 0.0
        return round(filled_fields / total_fields * 100, 2)

    def _is_field_filled(self, value: Any) -> bool:
        """判断字段是否已填写"""
        if value is None:
            return False
        if isinstance(value, list):
            return len([v for v in value if v and str(v).strip()]) > 0
        if isinstance(value, str):
            return bool(value.strip())
        return bool(value)

    def _get_improvement_suggestions(self, canvas: dict) -> List[str]:
        """根据画布内容生成改进建议"""
        suggestions = []
        score = self.calculate_model_score(canvas)

        if score < 50:
            suggestions.append("画布完成度较低，建议先完善核心字段")
        if score < 80:
            suggestions.append("可以进一步细化每个字段的内容")
        if "problem" in canvas and not canvas["problem"]:
            suggestions.append("建议补充目标客户的痛点问题")
        if "unique_value_proposition" in canvas and not canvas["unique_value_proposition"]:
            suggestions.append("独特价值主张是关键，建议重点思考")
        if "revenue_streams" in canvas and not canvas["revenue_streams"]:
            suggestions.append("收入来源是商业模式的核心，建议明确")

        return suggestions if suggestions else ["画布内容较完整，可以开始验证"]

    def _get_lean_canvas_template(self) -> dict:
        """获取精益画布空白模板"""
        return {
            "problem": [{"rank": 1, "title": "", "percentage": 0}],
            "solution": [{"title": ""}],
            "unique_value_proposition": "",
            "unfair_advantage": [""],
            "key_metrics": [""],
            "channels": [""],
            "cost_structure": "",
            "revenue_streams": [""]
        }

    def _get_business_model_template(self) -> dict:
        """获取商业模式画布空白模板"""
        return {
            "customer_segments": [""],
            "value_propositions": [""],
            "channels": [""],
            "customer_relationships": [""],
            "revenue_streams": [""],
            "key_resources": [""],
            "key_activities": [""],
            "key_partners": [""],
            "cost_structure": ""
        }

    def _get_value_proposition_template(self) -> dict:
        """获取价值主张画布空白模板"""
        return {
            "customer_jobs": [""],
            "pains": [""],
            "gains": [""],
            "products_services": [""],
            "gain_creators": [""],
            "pain_relievers": [""]
        }