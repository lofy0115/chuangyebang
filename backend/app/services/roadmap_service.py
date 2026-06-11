"""
落地路径规划引擎 - 根据痛点和利润模式生成可执行路线图
功能：分阶段任务规划、里程碑设定、风险识别、资源配置建议
"""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class RoadmapPhase:
    phase: int
    name: str
    duration_weeks: int
    goal: str
    tasks: List[Dict]
    milestones: List[str]
    risks: List[str]
    resources: List[str]
    budget: float


class RoadmapService:
    def generate_roadmap(self, pain_point: Dict, profit_model: Dict, params: Dict) -> Dict:
        """生成完整的落地路径"""
        pain_name = pain_point.get("name", "")
        model_key = profit_model.get("model_key", "product_sales")
        model_name = profit_model.get("model_name", "产品销售")

        phases = self._build_phases(pain_name, model_key, params)

        return {
            "overview": {
                "pain_point": pain_name,
                "profit_model": model_name,
                "total_duration_weeks": sum(p["duration_weeks"] for p in phases),
                "total_budget": sum(p["budget"] for p in phases),
                "phases_count": len(phases)
            },
            "phases": phases,
            "milestones": self._extract_milestones(phases),
            "risks": self._identify_risks(pain_name, model_key),
            "success_metrics": self._get_success_metrics(model_key)
        }

    def _build_phases(self, pain_name: str, model_key: str, params: Dict) -> List[Dict]:
        phases = []

        if model_key == "subscription":
            phases = [
                {
                    "phase": 1,
                    "name": "MVP验证期",
                    "duration_weeks": 4,
                    "goal": "验证核心价值假设，确认用户愿意付费",
                    "tasks": [
                        {"task": "明确目标用户画像", "description": "通过爬取的抱怨数据分析核心用户群体特征", "deliverable": "用户画像文档"},
                        {"task": "构建MVP", "description": "开发最简可行产品，包含核心功能解决目标痛点", "deliverable": "可运行的MVP产品"},
                        {"task": "获取首批10-20名付费用户", "description": "通过社群、私域流量获取种子用户，定价99-299元", "deliverable": "首批付费用户名单"},
                        {"task": "收集用户反馈", "description": "深度访谈5-10个用户，确认价值假设", "deliverable": "用户访谈报告"}
                    ],
                    "milestones": ["第2周：MVP上线", "第3周：首批用户付费", "第4周：用户访谈完成"],
                    "risks": ["用户不愿意付费", "产品价值不清晰", "获取成本过高"],
                    "resources": ["1名产品经理", "1-2名开发", "5000元营销预算"],
                    "budget": 30000
                },
                {
                    "phase": 2,
                    "name": "产品打磨期",
                    "duration_weeks": 6,
                    "goal": "根据用户反馈迭代产品，提升留存率",
                    "tasks": [
                        {"task": "产品迭代", "description": "基于用户反馈修复核心问题，每周发布一个版本", "deliverable": "4次产品迭代"},
                        {"task": "建立用户成功体系", "description": "配置客服和用户成功团队，主动跟进用户使用情况", "deliverable": "用户成功SOP"},
                        {"task": "流失率监控", "description": "建立数据看板，追踪周流失率，目标<8%/月", "deliverable": "留存数据看板"},
                        {"task": "社群运营", "description": "建立用户社群，增强用户粘性", "deliverable": "活跃用户社群"}
                    ],
                    "milestones": ["第6周：月流失率<8%", "第8周：用户满意度>80%"],
                    "risks": ["流失率过高", "用户反馈收集不及时", "竞争对手抄袭"],
                    "resources": ["1名产品经理", "2名开发", "1名客服", "15000元预算"],
                    "budget": 60000
                },
                {
                    "phase": 3,
                    "name": "规模化增长期",
                    "duration_weeks": 8,
                    "goal": "系统性获取用户，实现月收入快速增长",
                    "tasks": [
                        {"task": "增长渠道测试", "description": "测试SEO、内容营销、付费广告、社群裂变等渠道", "deliverable": "各渠道ROI分析报告"},
                        {"task": "优化获客成本", "description": "找到CAC<150元的获客渠道，稳定在目标范围内", "deliverable": "获客成本<150元"},
                        {"task": "建立内容营销体系", "description": "围绕痛点创建内容，吸引自然流量", "deliverable": "月均5篇高质量内容"},
                        {"task": "老带新裂变", "description": "设计老用户推荐奖励机制", "deliverable": "推荐系统上线"},
                        {"task": "付费用户达100+", "description": "实现月ARR>10万", "deliverable": "100名付费用户"}
                    ],
                    "milestones": ["第12周：CAC<150元", "第14周：月收入>5万", "第16周：月收入>10万"],
                    "risks": ["获客成本过高", "渠道红利消退", "团队执行力不足"],
                    "resources": ["增长负责人", "内容团队", "广告预算5万"],
                    "budget": 100000
                },
                {
                    "phase": 4,
                    "name": "商业化成熟期",
                    "duration_weeks": 8,
                    "goal": "优化单位经济，建立竞争壁垒",
                    "tasks": [
                        {"task": "单位经济优化", "description": "提升LTV/CAC比至>3，降低流失率至<5%", "deliverable": "单位经济达标"},
                        {"task": "产品矩阵扩展", "description": "基于核心用户需求开发增值服务/高级功能", "deliverable": "2个增值产品上线"},
                        {"task": "品牌建设", "description": "建立行业口碑和品牌认知", "deliverable": "行业媒体曝光3+篇"},
                        {"task": "团队扩充", "description": "招聘核心岗位，建立组织能力", "deliverable": "团队规模翻倍"},
                        {"task": "月收入稳定在20万+", "description": "实现可持续盈利", "deliverable": "月ARR>20万"}
                    ],
                    "milestones": ["第20周：LTV/CAC>3", "第22周：月流失率<5%", "第24周：月收入>20万"],
                    "risks": ["组织管理挑战", "竞争加剧", "政策监管风险"],
                    "resources": ["管理层扩充", "运营团队", "品牌预算"],
                    "budget": 150000
                }
            ]

        elif model_key == "freemium":
            phases = [
                {
                    "phase": 1,
                    "name": "产品/Market Fit验证",
                    "duration_weeks": 4,
                    "goal": "找到-product/market fit，确保免费用户愿意使用",
                    "tasks": [
                        {"task": "确定核心免费功能", "description": "明确什么功能免费，什么功能付费", "deliverable": "功能分层设计"},
                        {"task": "开发MVP", "description": "快速开发核心产品，上线后获取1000+免费用户", "deliverable": "1000+注册用户"},
                        {"task": "激活率优化", "description": "追踪新用户激活率，优化 onboarding流程，目标>40%", "deliverable": "激活率>40%"},
                        {"task": "确定目标转化率", "description": "通过小规模测试确定自然转化率，目标2-5%", "deliverable": "转化率数据"}
                    ],
                    "milestones": ["第2周：产品上线", "第4周：1000+注册用户"],
                    "risks": ["用户不愿意注册", "激活率过低", "产品价值不清晰"],
                    "resources": ["产品+开发团队", "初始推广预算5000元"],
                    "budget": 25000
                },
                {
                    "phase": 2,
                    "name": "增长引擎构建",
                    "duration_weeks": 6,
                    "goal": "建立可持续的用户增长系统",
                    "tasks": [
                        {"task": "SEO+内容增长", "description": "围绕用户痛点建立内容体系，获取自然流量", "deliverable": "月自然流量1万+"},
                        {"task": "裂变增长", "description": "设计分享奖励机制，让用户主动传播", "deliverable": "裂变系数>0.3"},
                        {"task": "社群裂变", "description": "通过种子用户社群实现快速传播", "deliverable": "3个500人社群"},
                        {"task": "转化率优化", "description": "A/B测试付费转化路径，目标转化率提升至3%+", "deliverable": "转化率3%+"}
                    ],
                    "milestones": ["第6周：月自然流量1万+", "第8周：付费用户50+"],
                    "risks": ["增长停滞", "转化率过低", "用户流失"],
                    "resources": ["增长负责人", "内容团队", "运营预算3万"],
                    "budget": 50000
                },
                {
                    "phase": 3,
                    "name": "规模化变现",
                    "duration_weeks": 8,
                    "goal": "通过广告+付费转化实现收入规模化",
                    "tasks": [
                        {"task": "广告系统接入", "description": "接入广告平台，优化eCPM", "deliverable": "eCPM>20元"},
                        {"task": "付费转化优化", "description": "提升付费转化率至5%+", "deliverable": "付费用户200+"},
                        {"task": "DAU达10万+", "description": "通过多渠道实现用户规模快速增长", "deliverable": "DAU10万+"},
                        {"task": "月收入稳定在10万+", "description": "广告+付费双轮驱动", "deliverable": "月收入10万+"}
                    ],
                    "milestones": ["第12周：DAU5万+", "第14周：月收入5万+", "第16周：月收入10万+"],
                    "risks": ["广告收入波动", "用户质量下降", "平台政策变化"],
                    "resources": ["运营团队", "广告优化师", "增长预算8万"],
                    "budget": 100000
                }
            ]

        elif model_key == "product_sales":
            phases = [
                {
                    "phase": 1,
                    "name": "产品开发",
                    "duration_weeks": 6,
                    "goal": "开发解决目标痛点的高品质产品",
                    "tasks": [
                        {"task": "市场调研", "description": "通过爬取的抱怨数据深入了解竞品和用户需求", "deliverable": "竞品分析报告"},
                        {"task": "产品设计", "description": "围绕痛点设计差异化的核心产品", "deliverable": "产品设计文档"},
                        {"task": "产品开发", "description": "敏捷开发，6周内出可销售版本", "deliverable": "可销售产品"},
                        {"task": "品控体系", "description": "建立产品质量控制流程，确保不出现同类痛点", "deliverable": "品控SOP"}
                    ],
                    "milestones": ["第4周：内测版本", "第6周：正式销售版本"],
                    "risks": ["开发延期", "产品质量不达标", "成本超支"],
                    "resources": ["产品+研发团队", "品控负责人"],
                    "budget": 60000
                },
                {
                    "phase": 2,
                    "name": "销售验证",
                    "duration_weeks": 4,
                    "goal": "验证产品能卖出去，测试销售渠道",
                    "tasks": [
                        {"task": "首批销售", "description": "通过私域、社群等渠道获取首批50-100个付费客户", "deliverable": "50+付费客户"},
                        {"task": "销售渠道测试", "description": "测试线上（电商/私域）+线下（代理/门店）渠道", "deliverable": "渠道ROI报告"},
                        {"task": "口碑收集", "description": "收集真实用户反馈，验证产品价值", "deliverable": "用户口碑案例3+"},
                        {"task": "复购验证", "description": "测试30天复购率，目标>20%", "deliverable": "复购率数据"}
                    ],
                    "milestones": ["第8周：50+付费客户", "第10周：复购率>20%"],
                    "risks": ["销售不及预期", "获客成本过高", "产品质量问题"],
                    "resources": ["销售团队", "客服团队", "营销预算2万"],
                    "budget": 40000
                },
                {
                    "phase": 3,
                    "name": "规模化销售",
                    "duration_weeks": 8,
                    "goal": "建立稳定的销售渠道，实现月销百万",
                    "tasks": [
                        {"task": "线上渠道扩张", "description": "天猫/京东/抖音电商全面铺开", "deliverable": "月GMV50万+"},
                        {"task": "代理渠道建设", "description": "发展区域代理，建立分销网络", "deliverable": "10+代理商"},
                        {"task": "品牌建设", "description": "通过口碑营销建立品牌知名度", "deliverable": "月销售100万+"},
                        {"task": "产品线扩展", "description": "基于核心用户需求扩展产品线", "deliverable": "3个SKU"}
                    ],
                    "milestones": ["第14周：月GMV50万+", "第16周：月销售100万+"],
                    "risks": ["渠道冲突", "价格战", "库存积压"],
                    "resources": ["销售团队扩充", "电商运营", "品牌预算"],
                    "budget": 150000
                }
            ]

        else:
            # 通用模板
            phases = [
                {
                    "phase": 1,
                    "name": "启动期",
                    "duration_weeks": 4,
                    "goal": "完成基础建设，准备MVP",
                    "tasks": [
                        {"task": "需求分析", "description": "基于痛点分析明确产品方向", "deliverable": "产品需求文档"},
                        {"task": "团队组建", "description": "招募核心团队成员", "deliverable": "核心团队到位"},
                        {"task": "MVP开发", "description": "4周内完成MVP", "deliverable": "MVP上线"}
                    ],
                    "milestones": ["第4周：MVP上线"],
                    "risks": ["团队组建困难", "开发延期"],
                    "resources": ["核心团队3-5人"],
                    "budget": 50000
                },
                {
                    "phase": 2,
                    "name": "验证期",
                    "duration_weeks": 6,
                    "goal": "验证产品价值和商业模式",
                    "tasks": [
                        {"task": "获取首批用户", "description": "通过各种渠道获取100名用户", "deliverable": "100名用户"},
                        {"task": "产品迭代", "description": "基于反馈快速迭代", "deliverable": "周级迭代"},
                        {"task": "商业模式验证", "description": "确认单位经济可行", "deliverable": "单位经济达标"}
                    ],
                    "milestones": ["第6周：100名用户", "第10周：单位经济验证"],
                    "risks": ["用户获取困难", "产品方向偏差"],
                    "resources": ["增长+运营"],
                    "budget": 80000
                },
                {
                    "phase": 3,
                    "name": "增长期",
                    "duration_weeks": 8,
                    "goal": "规模化增长，实现盈利",
                    "tasks": [
                        {"task": "增长提速", "description": "放大有效获客渠道", "deliverable": "月增长30%+"},
                        {"task": "商业化放大", "description": "实现月收入稳定增长", "deliverable": "月收入50万+"},
                        {"task": "团队建设", "description": "完善组织架构", "deliverable": "团队规模达标"}
                    ],
                    "milestones": ["第14周：月收入20万+", "第18周：月收入50万+"],
                    "risks": ["增长停滞", "管理失控"],
                    "resources": ["全员扩张"],
                    "budget": 200000
                }
            ]

        return phases

    def _extract_milestones(self, phases: List[Dict]) -> List[Dict]:
        milestones = []
        week_accum = 0
        for phase in phases:
            week_accum += phase["duration_weeks"]
            for ms in phase["milestones"]:
                milestones.append({
                    "week": week_accum,
                    "milestone": ms,
                    "phase": phase["name"]
                })
        return milestones

    def _identify_risks(self, pain_name: str, model_key: str) -> List[Dict]:
        common_risks = [
            {"risk": "用户获取成本高于预期", "likelihood": "高", "impact": "中", "mitigation": "先小规模测试渠道ROI再放大"},
            {"risk": "团队执行力不足", "likelihood": "中", "impact": "高", "mitigation": "设置周检视机制，及时调整"},
            {"risk": "竞争对手快速跟进", "likelihood": "高", "impact": "中", "mitigation": "快速迭代建立先发优势"},
        ]

        model_specific = {
            "subscription": [
                {"risk": "流失率过高（>10%/月）", "likelihood": "高", "impact": "高", "mitigation": "建立用户成功体系，主动跟进"},
            ],
            "freemium": [
                {"risk": "转化率过低（<1%）", "likelihood": "高", "impact": "中", "mitigation": "优化付费功能设计，加强onboarding"},
            ],
            "product_sales": [
                {"risk": "库存积压", "likelihood": "中", "impact": "高", "mitigation": "先预售再生产，控制首批量"},
            ],
            "platform_commission": [
                {"risk": "双边用户冷启动", "likelihood": "极高", "impact": "高", "mitigation": "先服务好一方再引另一方"},
            ],
        }

        risks = common_risks.copy()
        if model_key in model_specific:
            risks.extend(model_specific[model_key])
        return risks

    def _get_success_metrics(self, model_key: str) -> Dict:
        metrics = {
            "subscription": {
                "monthly_recurring_revenue": "月ARR>20万",
                "customer_churn_rate": "月流失率<5%",
                "ltv_cac_ratio": "LTV/CAC > 3",
                "payback_period": "回收期<3个月",
                "net_promoter_score": "NPS>40"
            },
            "freemium": {
                "dau": "DAU>10万",
                "conversion_rate": "付费转化率>3%",
                "free_to_paid_ratio": "付费率>5%",
                "ecpm": "eCPM>25元",
                "monthly_revenue": "月收入>10万"
            },
            "product_sales": {
                "monthly_gmv": "月GMV>100万",
                "gross_margin": "毛利率>40%",
                "customer_acquisition_cost": "CAC<100元",
                "repeat_purchase_rate": "复购率>30%",
                "inventory_turnover": "库存周转>6次/年"
            },
            "platform_commission": {
                "gmv": "月GMV>500万",
                "take_rate": "佣金率>5%",
                "active_sellers": "活跃商家>100",
                "active_buyers": "活跃买家>10000"
            }
        }
        return metrics.get(model_key, {
            "revenue": "月收入目标",
            "customers": "客户数目标",
            "margin": "毛利率目标"
        })

    def generate_roadmap_summary(self, roadmap: Dict) -> str:
        """生成文字版路线图摘要"""
        phases = roadmap["phases"]
        total_weeks = roadmap["overview"]["total_duration_weeks"]
        total_budget = roadmap["overview"]["total_budget"]

        summary = f"## {roadmap['overview']['pain_point']} → {roadmap['overview']['profit_model']} 落地路线图\n\n"
        summary += f"**总周期**: {total_weeks}周（约{total_weeks//4}个月）\n"
        summary += f"**总预算**: {total_budget:,}元\n\n"

        for phase in phases:
            summary += f"### 阶段{phase['phase']}: {phase['name']}（{phase['duration_weeks']}周）\n"
            summary += f"**目标**: {phase['goal']}\n"
            summary += f"**预算**: {phase['budget']:,}元\n"
            summary += f"**关键任务**:\n"
            for task in phase["tasks"]:
                summary += f"- {task['task']}: {task['description']}\n"
            summary += "\n"

        return summary