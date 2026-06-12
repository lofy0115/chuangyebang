import "package:flutter/material.dart";

class LeanCanvasScreen extends StatelessWidget {
  final String query;
  const LeanCanvasScreen({super.key, required this.query});

  @override
  Widget build(BuildContext context) {
    final canvas = _getLeanCanvasData(query);

    return Scaffold(
      appBar: AppBar(title: Text('🎯 精益画布 - $query')),
      body: Container(
        color: const Color(0xFF0f0f23),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              _buildCell('问题', canvas['problem']!, Colors.red.shade400),
              _buildCell('解决方案', canvas['solution']!, Colors.blue.shade400),
              _buildCell('独特价值主张', canvas['uniqueValue']!, Colors.purple.shade400),
              _buildCell('门槛优势', canvas['unfairAdvantage']!, Colors.orange.shade400),
              _buildCell('关键指标', canvas['keyMetrics']!, Colors.teal.shade400),
              _buildCell('渠道', canvas['channels']!, Colors.cyan.shade400),
              _buildCell('成本结构', canvas['costStructure']!, Colors.grey.shade400),
              _buildCell('收入来源', canvas['revenueStreams']!, Colors.green.shade400),
            ],
          ),
        ),
      ),
    );
  }

  Map<String, String> _getLeanCanvasData(String query) {
    final allData = {
      '母婴': {
        'problem': '质量安全担忧、价格不透明、品牌选择困难、正品担忧',
        'solution': '建立质量溯源体系、引入专家评测、提供比价工具、一键查真伪',
        'uniqueValue': '让妈妈买得放心，孩子用得安心',
        'unfairAdvantage': '独家质量评测体系、专家入驻内容、用户真实评价社区',
        'keyMetrics': '复购率、NPS评分、专家内容互动率、质量投诉率',
        'channels': '小红书种草、妈妈群推广、电商平台、内容电商',
        'costStructure': '内容制作+质控+客服+物流',
        'revenueStreams': '产品销售佣金、知识付费、广告推广、会员订阅',
      },
      '美妆': {
        'problem': '不知道适合什么产品、成分不安全、效果不明显、购买决定困难',
        'solution': 'AI肤质测试、成分分析对比、效果可视化、小样试用',
        'uniqueValue': '找到最适合自己的美妆产品',
        'unfairAdvantage': 'AI肤质分析、真实用户效果数据库、成分安全预警',
        'keyMetrics': '转化购买率、试用转化率、内容分享率、复购率',
        'channels': '小红书、抖音、B站、微信小程序',
        'costStructure': 'AI研发+内容制作+小样采购+配送',
        'revenueStreams': '产品销售分成、品牌广告、试用样品、会员订阅',
      },
      '智能家居': {
        'problem': '操作复杂难上手、设备之间不兼容、隐私安全隐患、稳定性差经常掉线',
        'solution': '一键配对教程、跨平台互联方案、隐私安全报告、稳定性监控',
        'uniqueValue': '让智能家居真正智能又安全',
        'unfairAdvantage': '跨品牌互联协议、隐私安全认证、7x24监控',
        'keyMetrics': '设备在线率、问题解决率、用户满意度、续费率',
        'channels': '知乎测评、抖音演示、厂商合作、花粉俱乐部',
        'costStructure': '技术研发+安全认证+客服+服务器',
        'revenueStreams': '互联解决方案收费、安全认证服务、数据洞察、厂商合作',
      },
      '新能源汽车': {
        'problem': '续航虚标严重、充电不方便、售后推诿、智能功能鸡肋',
        'solution': '真实续航测试、充电桩地图+预约、售后评分机制、智驾功能评测',
        'uniqueValue': '帮车主选对车、避坑指南',
        'unfairAdvantage': '真实车主评测、充电桩实时数据、售后评分体系',
        'keyMetrics': '内容阅读量、帮购转化、充电使用率、投诉解决率',
        'channels': '微博、知乎、抖音、车友群',
        'costStructure': '内容制作+数据采集+客服+线下活动',
        'revenueStreams': '推荐购车佣金、充电服务分成、广告、会员服务',
      },
      '食品': {
        'problem': '食品安全担忧、不知道是否新鲜、营养成分不透明、价格波动大',
        'solution': '溯源系统、新鲜度实时监测、营养成分解读、价格提醒',
        'uniqueValue': '每一口都吃得明明白白',
        'unfairAdvantage': '全程溯源、实时新鲜度监测、营养师解读',
        'keyMetrics': '扫码率、溯源查询量、会员复购、问题发现率',
        'channels': '电商平台、超市合作、直播带货、社区团购',
        'costStructure': '溯源系统+检测设备+物流合作+内容制作',
        'revenueStreams': '溯源服务费、检测认证费、优质食品销售、品牌合作',
      },
      'SaaS': {
        'problem': '功能学习成本高、客服响应慢、数据迁移困难、价格不透明/贵',
        'solution': 'AI客服+操作引导、7x24在线支持、一键数据导出、按需付费模式',
        'uniqueValue': '让企业省心、省钱、真正用起来',
        'unfairAdvantage': 'AI辅助功能、无缝迁移工具、透明定价',
        'keyMetrics': '活跃使用率、客服首次响应时间、续费率、NPS',
        'channels': '官网SEO、行业大会、客户推荐、应用市场',
        'costStructure': '研发+AI算力+客服+服务器+销售',
        'revenueStreams': '订阅费、增值功能、实施服务、生态分成',
      },
    };

    return allData[query] ?? allData['母婴']!;
  }

  Widget _buildCell(String title, String content, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1a1a3e),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(content, style: const TextStyle(color: Colors.white, fontSize: 14)),
        ],
      ),
    );
  }
}