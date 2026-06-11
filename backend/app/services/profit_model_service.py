"""
利润模式设计引擎 - 基于痛点的利润模式推荐与单位经济计算
功能：推荐最适利润模式、计算单位经济、预测收入、对比方案
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import math


@dataclass
class ProfitModel:
    key: str
    name: str
    description: str
    applicability: str
    implementation_difficulty: str
    initial_cost: float
    revenue_model: str
    scalability: str


@dataclass
class UnitEconomics:
    cac: float          # 客户获取成本（元）
    ltv: float          # 客户终身价值（元）
    arpu: float         # 月均收入（元/用户/月）
    gross_margin: float # 毛利率（%）
    churn_rate: float   # 月流失率（%）
    payback_months: float  # 回收期（月）
    ltv_cac_ratio: float   # LTV/CAC比率
    break_even_customers: int  # 盈亏平衡客户数
    monthly_breakeven: float  # 月盈亏平衡收入


@dataclass
class RevenueForecast:
    month: int
    customers: int
    revenue: float
    cost: float
    profit: float
    cumulative_profit: float


class ProfitModelService:
    MODELS = {
        "product_sales": ProfitModel(
            key="product_sales",
            name="产品销售",
            description="直接销售实体或数字产品，一次性获得收入",
            applicability="适合解决'质量差''功能少''价格贵'等痛点，通过高品质差异化产品获得溢价",
            implementation_difficulty="中等（需要产品开发和销售渠道）",
            initial_cost=50000,
            revenue_model="单品毛利=售价-成本，毛利率通常30-60%",
            scalability="中等（受限于产能和渠道）"
        ),
        "subscription": ProfitModel(
            key="subscription",
            name="订阅制服务",
            description="用户按月/年付费，持续获得服务",
            applicability="适合解决'服务差''功能少''售后难'等痛点，建立持续现金流",
            implementation_difficulty="较高（需要持续提供用户价值）",
            initial_cost=100000,
            revenue_model="月/年订阅费，LTV=月费×平均订阅月数，流失率决定LTV",
            scalability="高（边际成本低，可快速扩张）"
        ),
        "freemium": ProfitModel(
            key="freemium",
            name="免费增值",
            description="基础功能免费，高级功能付费",
            applicability="适合解决'价格贵''功能少'等痛点，通过免费吸引大量用户转化付费",
            implementation_difficulty="中等（需要平衡免费和付费功能）",
            initial_cost=80000,
            revenue_model="免费用户靠广告或少量转化付费，付费率通常2-5%",
            scalability="高（可快速获取海量用户）"
        ),
        "platform_commission": ProfitModel(
            key="platform_commission",
            name="平台佣金",
            description="搭建平台连接供需双方，抽取佣金",
            applicability="适合解决'物流慢''质量差'等行业痛点，通过平台化整合产业链",
            implementation_difficulty="高（需要双边用户基础）",
            initial_cost=200000,
            revenue_model="交易额×佣金比例，通常3-15%",
            scalability="极高（网络效应）"
        ),
        "data_service": ProfitModel(
            key="data_service",
            name="数据服务",
            description="收集分析数据，为企业提供洞察服务",
            applicability="适合有独特数据源的场景，通过数据价值变现",
            implementation_difficulty="高（需要独特数据源和数据处理能力）",
            initial_cost=150000,
            revenue_model="数据订阅费或按次查询收费，毛利率高达80%+",
            scalability="高（数据可复用）"
        ),
        "tech_licensing": ProfitModel(
            key="tech_licensing",
            name="技术授权",
            description="将技术/专利授权给他人使用",
            applicability="适合有技术壁垒的创新，解决'功能少''质量差'痛点",
            implementation_difficulty="高（需要技术壁垒和IP保护）",
            initial_cost=120000,
            revenue_model="授权费+ royalties，通常一次性授权费+销售额5-15%",
            scalability="中等（受限于IP可授权次数）"
        ),
        "advertising": ProfitModel(
            key="advertising",
            name="广告变现",
            description="通过广告展示获得收入",
            applicability="适合高流量平台，解决'价格贵''功能少'痛点",
            implementation_difficulty="低（变现模式成熟）",
            initial_cost=30000,
            revenue_model="CPM/CPC/CPA广告收入，eCPM通常5-50元",
            scalability="极高（依赖流量规模）"
        ),
    }

    PAIN_POINT_MODEL_MAP = {
        "物流配送": ["platform_commission", "product_sales"],
        "商品质量": ["product_sales", "subscription"],
        "售后服务": ["subscription", "freemium"],
        "价格问题": ["freemium", "product_sales", "advertising"],
        "功能体验": ["freemium", "subscription", "tech_licensing"],
        "虚假宣传": ["subscription", "freemium"],
        "食品安全": ["product_sales", "subscription", "data_service"],
        "个人信息": ["freemium", "advertising"],
        "虚假评价": ["platform_commission", "data_service"],
    }

    def recommend_model(self, pain_point: Dict) -> Dict:
        """根据痛点推荐最合适的利润模式"""
        pain_name = pain_point.get("name", "")
        intensity = pain_point.get("intensity", 0.5)
        unmet_score = pain_point.get("unmet_score", 0)
        frequency = pain_point.get("frequency", 1)

        # 找出匹配的利润模式
        matched_keys = []
        for pp_key, model_keys in self.PAIN_POINT_MODEL_MAP.items():
            if pp_key in pain_name:
                matched_keys.extend(model_keys)

        if not matched_keys:
            matched_keys = ["product_sales", "freemium", "subscription"]

        # 去重并排序（优先推荐匹配度高的）
        matched_keys = list(dict.fromkeys(matched_keys))

        recommendations = []
        for key in matched_keys[:3]:
            model = self.MODELS[key]
            score = 0.5

            # 根据痛点特性调整评分
            if "物流" in pain_name:
                if key == "platform_commission":
                    score += 0.3
                if key == "product_sales":
                    score += 0.2
            if "质量" in pain_name:
                if key == "product_sales":
                    score += 0.3
                if key == "subscription":
                    score += 0.2
            if "售后" in pain_name:
                if key == "subscription":
                    score += 0.4
            if "价格" in pain_name:
                if key == "freemium":
                    score += 0.3
                if key == "advertising":
                    score += 0.2
            if "功能" in pain_name or "体验" in pain_name:
                if key == "subscription":
                    score += 0.3
                if key == "freemium":
                    score += 0.2
            if unmet_score > 0.4:
                if key == "subscription":
                    score += 0.2
            if intensity > 0.7:
                if key == "product_sales":
                    score += 0.15

            recommendations.append({
                "model": model.key,
                "name": model.name,
                "match_score": round(min(1.0, score), 2),
                "reason": model.applicability,
                "difficulty": model.implementation_difficulty,
                "initial_cost_estimate": model.initial_cost,
                "revenue_model": model.revenue_model,
                "scalability": model.scalability,
                "key_metric_target": self._get_metric_targets(model.key)
            })

        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "pain_point": pain_name,
            "pain_intensity": intensity,
            "unmet_score": unmet_score,
            "top_recommendation": recommendations[0] if recommendations else None,
            "alternatives": recommendations[1:],
            "all_models": [{"key": k, "name": v.name} for k, v in self.MODELS.items()]
        }

    def _get_metric_targets(self, model_key: str) -> Dict:
        """各模式的目标指标"""
        targets = {
            "product_sales": {"target_margin": "40%+", "target_conversion": "3-5%", "cac_range": "20-100"},
            "subscription": {"target_margin": "60%+", "target_churn": "<5%/月", "cac_range": "50-200"},
            "freemium": {"target_margin": "30%+", "target_conversion": "2-5%", "cac_range": "5-30"},
            "platform_commission": {"target_margin": "50%+", "target_take_rate": "5-15%", "cac_range": "100-500"},
            "data_service": {"target_margin": "80%+", "target_arppu": "500-5000", "cac_range": "200-1000"},
            "tech_licensing": {"target_margin": "70%+", "target_royalty": "5-15%", "cac_range": "50-200"},
            "advertising": {"target_margin": "40%+", "target_ecpm": "20-100", "cac_range": "1-10"},
        }
        return targets.get(model_key, {})

    def calculate_unit_economics(self, model_key: str, params: Dict) -> Dict:
        """计算单位经济"""
        model = self.MODELS.get(model_key)
        if not model:
            return {"error": "未知的利润模式"}

        result = {
            "model": model_key,
            "model_name": model.name,
            "inputs": params,
            "metrics": {}
        }

        # 产品销售模式
        if model_key == "product_sales":
            price = params.get("price", 299)
            cost = params.get("cost", 120)
            cac = params.get("cac", 50)
            marketing_spend = params.get("marketing_spend", 10000)
            expected_sales = params.get("expected_sales", 200)

            gross_margin = (price - cost) / price * 100
            ltv = price - cost  # 一次性，不考虑复购
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = cac / (price - cost) if price > cost else 999

            result["metrics"] = {
                "cac": cac,
                "ltv": round(ltv, 2),
                "arpu": round(price * expected_sales / max(1, marketing_spend / cac), 2),
                "gross_margin_pct": round(gross_margin, 1),
                "gross_profit_per_unit": round(price - cost, 2),
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "break_even_customers": math.ceil(cac / (price - cost) * 1.5) if price > cost else 999,
                "monthly_breakeven": round(cac * 1.5, 2),
                "recommendation": f"毛利率{gross_margin:.0f}%，需获取约{math.ceil(cac/(price-cost)*1.5)}个客户才能盈利"
            }

        # 订阅模式
        elif model_key == "subscription":
            monthly_fee = params.get("monthly_fee", 99)
            cost_per_user = params.get("cost_per_user", 20)
            cac = params.get("cac", 150)
            churn_rate = params.get("churn_rate", 0.05)

            gross_margin = (monthly_fee - cost_per_user) / monthly_fee * 100
            avg_lifetime_months = 1 / churn_rate if churn_rate > 0 else 12
            ltv = monthly_fee * avg_lifetime_months - cost_per_user * avg_lifetime_months
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = cac / (monthly_fee - cost_per_user) if monthly_fee > cost_per_user else 999

            result["metrics"] = {
                "cac": cac,
                "ltv": round(ltv, 2),
                "arpu": monthly_fee,
                "gross_margin_pct": round(gross_margin, 1),
                "churn_rate_pct": round(churn_rate * 100, 1),
                "avg_lifetime_months": round(avg_lifetime_months, 1),
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "break_even_customers": math.ceil(cac / (monthly_fee - cost_per_user) * 1.2) if monthly_fee > cost_per_user else 999,
                "monthly_breakeven": round(cac * 1.2 / (monthly_fee - cost_per_user) * monthly_fee, 2) if monthly_fee > cost_per_user else 999,
                "recommendation": f"月流失率{churn_rate*100:.1f}%，LTV/CAC={ltv_cac:.1f}，回收期{payback_months:.1f}个月"
            }

        # 免费增值模式
        elif model_key == "freemium":
            free_users = params.get("free_users", 10000)
            conversion_rate = params.get("conversion_rate", 0.03)
            paid_monthly_fee = params.get("paid_monthly_fee", 99)
            cost_per_user = params.get("cost_per_user", 5)
            cac = params.get("cac", 10)
            marketing_spend = params.get("marketing_spend", 10000)

            paid_users = free_users * conversion_rate
            gross_margin = (paid_monthly_fee - cost_per_user) / paid_monthly_fee * 100
            ltv = paid_monthly_fee * 12 - cost_per_user * 12  # 按年估算
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = cac / (paid_monthly_fee - cost_per_user) if paid_monthly_fee > cost_per_user else 999

            result["metrics"] = {
                "cac": cac,
                "ltv": round(ltv, 2),
                "free_users": free_users,
                "paid_users": round(paid_users, 0),
                "conversion_rate_pct": round(conversion_rate * 100, 1),
                "arpu": round(paid_users * paid_monthly_fee / free_users, 2),
                "gross_margin_pct": round(gross_margin, 1),
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "marketing_cost_per_paid_user": round(marketing_spend / max(1, paid_users), 2),
                "recommendation": f"转化率{conversion_rate*100:.1f}%，{free_users}免费用户转化{int(paid_users)}付费用户，月收入约{int(paid_users*paid_monthly_fee)}元"
            }

        # 平台佣金模式
        elif model_key == "platform_commission":
            gmv_month = params.get("gmv_month", 1000000)
            take_rate = params.get("take_rate", 0.08)
            platform_cost = params.get("platform_cost", 100000)
            cac = params.get("cac", 300)

            revenue = gmv_month * take_rate
            gross_margin = 80  # 平台模式毛利高
            ltv = revenue * 12  # 按年估算
            ltv_cac = ltv / cac / 12 if cac > 0 else 0  # 年化
            payback_months = cac / (revenue / max(1, platform_cost * 0.01)) if revenue > 0 else 999

            result["metrics"] = {
                "cac": cac,
                "gmv_month": gmv_month,
                "take_rate_pct": round(take_rate * 100, 1),
                "monthly_revenue": round(revenue, 2),
                "gross_margin_pct": gross_margin,
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "break_even_gmv": math.ceil(platform_cost / take_rate * 1.5) if take_rate > 0 else 999,
                "recommendation": f"月GMV{gmV:=gmv_month/10000:.0f}万，抽取{take_rate*100:.0f}%佣金，月收入约{revenue/10000:.1f}万，需GMV达{gmV*1.5:.0f}万才能盈亏平衡"
            }

        # 数据服务模式
        elif model_key == "data_service":
            clients = params.get("clients", 50)
            annual_fee = params.get("annual_fee", 50000)
            data_cost = params.get("data_cost", 50000)
            cac = params.get("cac", 500)

            revenue_year = clients * annual_fee
            gross_margin = (revenue_year - data_cost) / revenue_year * 100 if revenue_year > 0 else 0
            ltv = annual_fee * 3 - data_cost * 3 / clients if clients > 0 else 0
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = cac / (annual_fee / 12) if annual_fee > 0 else 999

            result["metrics"] = {
                "cac": cac,
                "clients": clients,
                "annual_fee_per_client": annual_fee,
                "annual_revenue": round(revenue_year, 2),
                "gross_margin_pct": round(gross_margin, 1),
                "ltv": round(ltv, 2),
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "recommendation": f"获取{clients}个企业客户，年费{annual_fee}元，年收入约{revenue_year/10000:.0f}万"
            }

        # 技术授权模式
        elif model_key == "tech_licensing":
            license_fee = params.get("license_fee", 100000)
            royalty_rate = params.get("royalty_rate", 0.10)
            expected_sales = params.get("expected_sales", 500000)
            rd_cost = params.get("rd_cost", 200000)
            cac = params.get("cac", 200)

            royalty_revenue = expected_sales * royalty_rate
            total_revenue = license_fee + royalty_revenue
            gross_margin = 70
            ltv = total_revenue
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = rd_cost / (license_fee / 12) if license_fee > 0 else 999

            result["metrics"] = {
                "cac": cac,
                "license_fee": license_fee,
                "royalty_rate_pct": round(royalty_rate * 100, 1),
                "expected_annual_sales": expected_sales,
                "annual_revenue": round(total_revenue, 2),
                "gross_margin_pct": gross_margin,
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "recommendation": f"一次性授权费{license_fee}元+销售额10%royalty，预计年总收入{total_revenue/10000:.0f}万"
            }

        # 广告变现模式
        elif model_key == "advertising":
            dau = params.get("dau", 100000)
            ecpm = params.get("ecpm", 30)
            cac = params.get("cac", 5)
            content_cost = params.get("content_cost", 50000)

            daily_revenue = dau * ecpm / 1000
            monthly_revenue = daily_revenue * 30
            gross_margin = (monthly_revenue - content_cost) / monthly_revenue * 100 if monthly_revenue > 0 else 0
            ltv = monthly_revenue * 12
            ltv_cac = ltv / cac if cac > 0 else 0
            payback_months = cac / daily_revenue if daily_revenue > 0 else 999

            result["metrics"] = {
                "cac": cac,
                "dau": dau,
                "ecpm": ecpm,
                "daily_revenue": round(daily_revenue, 2),
                "monthly_revenue": round(monthly_revenue, 2),
                "gross_margin_pct": round(gross_margin, 1),
                "ltv": round(ltv, 2),
                "ltv_cac_ratio": round(ltv_cac, 2),
                "payback_months": round(payback_months, 1),
                "recommendation": f"DAU{dau/10000:.0f}万，eCPM{ecpm}元，月收入约{monthly_revenue/10000:.1f}万，需DAU达{payback_months*1000/ecpm*30:.0f}才能当天回本"
            }

        return result

    def forecast_revenue(self, model_key: str, params: Dict, months: int = 12) -> List[Dict]:
        """12个月收入预测"""
        forecasts = []

        if model_key == "subscription":
            monthly_fee = params.get("monthly_fee", 99)
            cost_per_user = params.get("cost_per_user", 20)
            initial_customers = params.get("initial_customers", 100)
            growth_rate = params.get("monthly_growth_rate", 0.15)
            churn_rate = params.get("churn_rate", 0.05)
            marketing_budget = params.get("marketing_budget", 10000)

            customers = initial_customers
            cumulative_profit = 0
            cac_total = 0

            for m in range(1, months + 1):
                new_customers = int(customers * growth_rate)
                churned = int(customers * churn_rate)
                customers = customers + new_customers - churned
                cac = new_customers * (marketing_budget / max(1, initial_customers))
                cac_total += cac

                revenue = customers * monthly_fee
                cost = customers * cost_per_user + cac
                profit = revenue - cost
                cumulative_profit += profit

                forecasts.append({
                    "month": m,
                    "customers": customers,
                    "new_customers": new_customers,
                    "churned": churned,
                    "revenue": round(revenue, 2),
                    "cost": round(cost, 2),
                    "profit": round(profit, 2),
                    "cumulative_profit": round(cumulative_profit, 2),
                    "cac": round(cac, 2)
                })

        elif model_key == "freemium":
            free_users = params.get("free_users", 10000)
            conversion_rate = params.get("conversion_rate", 0.03)
            paid_monthly_fee = params.get("paid_monthly_fee", 99)
            cost_per_user = params.get("cost_per_user", 5)
            growth_rate = params.get("monthly_growth_rate", 0.10)

            customers = 0
            cumulative_profit = 0

            for m in range(1, months + 1):
                free_users = int(free_users * (1 + growth_rate))
                new_paid = int(free_users * conversion_rate)
                customers = customers + new_paid

                revenue = customers * paid_monthly_fee
                cost = free_users * cost_per_user + new_paid * 10
                profit = revenue - cost
                cumulative_profit += profit

                forecasts.append({
                    "month": m,
                    "free_users": free_users,
                    "paid_customers": customers,
                    "new_paid": new_paid,
                    "revenue": round(revenue, 2),
                    "cost": round(cost, 2),
                    "profit": round(profit, 2),
                    "cumulative_profit": round(cumulative_profit, 2)
                })

        elif model_key == "product_sales":
            price = params.get("price", 299)
            cost = params.get("cost", 120)
            cac = params.get("cac", 50)
            initial_sales = params.get("initial_monthly_sales", 100)
            growth_rate = params.get("monthly_growth_rate", 0.20)

            sales = initial_sales
            cumulative_profit = 0

            for m in range(1, months + 1):
                sales = int(sales * (1 + growth_rate))
                revenue = sales * price
                cogs = sales * cost
                marketing = sales * cac
                cost_total = cogs + marketing
                profit = revenue - cost_total
                cumulative_profit += profit

                forecasts.append({
                    "month": m,
                    "sales": sales,
                    "revenue": round(revenue, 2),
                    "cogs": round(cogs, 2),
                    "marketing": round(marketing, 2),
                    "profit": round(profit, 2),
                    "cumulative_profit": round(cumulative_profit, 2)
                })

        else:
            # 默认简单预测
            base_revenue = params.get("base_revenue", 10000)
            growth_rate = params.get("growth_rate", 0.10)
            base_cost = params.get("base_cost", 8000)

            revenue = base_revenue
            cumulative_profit = 0

            for m in range(1, months + 1):
                revenue = revenue * (1 + growth_rate)
                cost = base_cost * (1 + growth_rate * 0.5)
                profit = revenue - cost
                cumulative_profit += profit

                forecasts.append({
                    "month": m,
                    "revenue": round(revenue, 2),
                    "cost": round(cost, 2),
                    "profit": round(profit, 2),
                    "cumulative_profit": round(cumulative_profit, 2)
                })

        return forecasts

    def compare_models(self, pain_point: Dict, model_keys: List[str]) -> Dict:
        """对比多个利润模式"""
        comparisons = []
        for key in model_keys:
            model = self.MODELS.get(key)
            if not model:
                continue

            rec = self.recommend_model({**pain_point, "name": pain_point.get("name", "")})
            unit_econ = self.calculate_unit_economics(key, self._default_params(key))

            comparisons.append({
                "model_key": key,
                "model_name": model.name,
                "match_score": next((r["match_score"] for r in rec["alternatives"] + [rec.get("top_recommendation", {})] if r.get("model") == key), 0.5),
                "difficulty": model.implementation_difficulty,
                "initial_cost": model.initial_cost,
                "unit_economics": unit_econ.get("metrics", {}),
                "pros": self._model_pros(key),
                "cons": self._model_cons(key),
                "best_for": model.applicability.split("，")[0] if "，" in model.applicability else model.applicability
            })

        comparisons.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "pain_point": pain_point.get("name", ""),
            "comparisons": comparisons,
            "recommended": comparisons[0] if comparisons else None
        }

    def _default_params(self, model_key: str) -> Dict:
        defaults = {
            "product_sales": {"price": 299, "cost": 120, "cac": 50, "marketing_spend": 10000, "expected_sales": 200},
            "subscription": {"monthly_fee": 99, "cost_per_user": 20, "cac": 150, "churn_rate": 0.05},
            "freemium": {"free_users": 10000, "conversion_rate": 0.03, "paid_monthly_fee": 99, "cost_per_user": 5, "cac": 10, "marketing_spend": 10000},
            "platform_commission": {"gmv_month": 1000000, "take_rate": 0.08, "platform_cost": 100000, "cac": 300},
            "data_service": {"clients": 50, "annual_fee": 50000, "data_cost": 50000, "cac": 500},
            "tech_licensing": {"license_fee": 100000, "royalty_rate": 0.10, "expected_sales": 500000, "rd_cost": 200000, "cac": 200},
            "advertising": {"dau": 100000, "ecpm": 30, "cac": 5, "content_cost": 50000},
        }
        return defaults.get(model_key, {})

    def _model_pros(self, key: str) -> List[str]:
        pros = {
            "product_sales": ["立即产生现金流", "模式简单易懂", "可控成本"],
            "subscription": ["可预测的经常性收入", "客户粘性高", "边际成本低"],
            "freemium": ["快速获取海量用户", "降低用户尝试门槛", "可转化为多种变现方式"],
            "platform_commission": ["轻资产模式", "网络效应", "规模化后利润率高"],
            "data_service": ["毛利率极高", "可复用性强", "客户付费意愿强"],
            "tech_licensing": ["IP可复用多次", "收入稳定", "可快速规模化"],
            "advertising": ["变现模式成熟", "规模化容易", "边际成本接近零"],
        }
        return pros.get(key, [])

    def _model_cons(self, key: str) -> List[str]:
        cons = {
            "product_sales": ["依赖渠道和流量", "需要库存和供应链管理", "复购率挑战"],
            "subscription": ["需要持续提供价值", "客户获取成本较高", "流失率控制关键"],
            "freemium": ["转化率通常较低", "需要大量用户基础", "广告收入波动大"],
            "platform_commission": ["需要双边用户基础", "冷启动困难", "需要持续运营"],
            "data_service": ["需要独特数据源", "隐私合规风险", "客户数量有限"],
            "tech_licensing": ["需要技术壁垒", "IP保护难度大", "授权谈判复杂"],
            "advertising": ["依赖流量质量", "广告主依赖风险", "用户体验影响"],
        }
        return cons.get(key, [])