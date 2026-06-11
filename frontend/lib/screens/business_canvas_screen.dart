import "package:flutter/material.dart";

class BusinessCanvasScreen extends StatelessWidget {
  final String query;
  const BusinessCanvasScreen({super.key, required this.query});

  @override
  Widget build(BuildContext context) {
    final canvas = _getBusinessCanvasData(query);

    return Scaffold(
      appBar: AppBar(title: Text('📋 商业模式画布 - $query')),
      body: Container(
        color: const Color(0xFF0f0f23),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(children: [
                Expanded(child: _buildCell('关键合作伙伴', canvas['keyPartners']!, Colors.blue)),
                Expanded(child: _buildCell('关键活动', canvas['keyActivities']!, Colors.teal)),
                Expanded(child: _buildCell('核心资源', canvas['keyResources']!, Colors.indigo)),
              ]),
              Row(children: [
                Expanded(child: _buildCell('价值主张', canvas['valuePropositions']!, Colors.purple)),
                Expanded(child: _buildCell('客户关系', canvas['customerRelationships']!, Colors.pink)),
                Expanded(child: _buildCell('渠道', canvas['channels']!, Colors.cyan)),
              ]),
              Row(children: [
                Expanded(child: _buildCell('客户细分', canvas['customerSegments']!, Colors.orange)),
                const Expanded(child: SizedBox()),
                const Expanded(child: SizedBox()),
              ]),
              const Divider(color: Colors.white24),
              Row(children: [
                Expanded(child: _buildCell('成本结构', canvas['costStructure']!, Colors.grey)),
                Expanded(child: _buildCell('收入来源', canvas['revenueStreams']!, Colors.green)),
                const Expanded(child: SizedBox()),
              ]),
            ],
          ),
        ),
      ),
    );
  }

  Map<String, String> _getBusinessCanvasData(String query) {
    final allData = {
      '母婴': {
        'keyPartners': '供应商,物流公司,仓储服务商',
        'keyActivities': '商品采购,仓储管理,配送服务,用户运营',
        'keyResources': '物流网络,技术平台,用户数据,品牌',
        'valuePropositions': '快速配送,正品保障,价格优惠,优质服务',
        'customerRelationships': '在线客服,会员体系,社区运营',
        'channels': '移动APP,微信小程序,线下门店,社交媒体',
        'customerSegments': '年轻上班族(25-35岁),家庭主妇(30-45岁),学生群体(18-25岁)',
        'costStructure': '物流成本40%,人力成本25%,营销成本15%,技术成本10%,其他10%',
        'revenueStreams': '商品销售80%,会员收入12%,广告收入8%',
      },
      '美妆': {
        'keyPartners': '品牌方,物流公司,内容创作者',
        'keyActivities': '选品,内容制作,仓储物流,用户运营',
        'keyResources': '内容数据库,用户数据,供应链',
        'valuePropositions': '找到适合自己的产品,真实评测,正品保障',
        'customerRelationships': '社区互动,专家咨询,会员体系',
        'channels': '小红书,抖音,微信,APP',
        'customerSegments': '成分党(38%),品牌导向型(32%),学生平价型(20%),礼品型(10%)',
        'costStructure': '内容制作35%,采购30%,营销20%,运营15%',
        'revenueStreams': '销售分成60%,广告25%,会员15%',
      },
      '智能家居': {
        'keyPartners': '设备厂商,平台商,解决方案商',
        'keyActivities': '设备互联,技术支持,数据整合',
        'keyResources': '互联协议,用户数据,技术支持团队',
        'valuePropositions': '跨品牌互联,稳定可靠,隐私安全',
        'customerRelationships': '技术支持,在线文档,社区论坛',
        'channels': '知乎,抖音,厂商合作,花粉俱乐部',
        'customerSegments': '科技爱好者(40%),实用性用户(35%),价格敏感型(15%),智能家庭用户(10%)',
        'costStructure': '研发40%,安全认证25%,客服20%,服务器15%',
        'revenueStreams': '解决方案费50%,数据服务30%,认证服务20%',
      },
      '新能源汽车': {
        'keyPartners': '车企,充电运营商,停车场',
        'keyActivities': '内容制作,数据采集,线下活动',
        'keyResources': '真实评测数据,车主社群,充电数据',
        'valuePropositions': '真实评测,帮买决策,充电便捷',
        'customerRelationships': '车友群,线下活动,专属顾问',
        'channels': '微博,知乎,抖音,车友群',
        'customerSegments': '环保主义者(35%),家庭用户(30%),运营用户(20%),科技极客(15%)',
        'costStructure': '内容制作30%,数据采集25%,线下活动25%,运营20%',
        'revenueStreams': '购车佣金40%,充电分成30%,广告20%,会员10%',
      },
      '食品': {
        'keyPartners': '农场,检测机构,物流公司',
        'keyActivities': '品质检测,溯源系统,仓储物流',
        'keyResources': '检测设备,溯源数据库,供应商关系',
        'valuePropositions': '安全健康,新鲜品质,营养透明',
        'customerRelationships': '会员体系,农场体验,营养师咨询',
        'channels': '电商平台,超市合作,直播带货,社区团购',
        'customerSegments': '健康导向型(38%),性价比型(32%),品质生活型(20%),家庭采购型(10%)',
        'costStructure': '检测设备20%,物流30%,营销25%,运营25%',
        'revenueStreams': '认证服务40%,销售分成35%,检测费25%',
      },
      'SaaS': {
        'keyPartners': '云服务商,集成商,渠道商',
        'keyActivities': '产品研发,客户成功,生态运营',
        'keyResources': '技术团队,用户数据,品牌',
        'valuePropositions': '功能完善,稳定快速,简单易用',
        'customerRelationships': '在线客服,成功团队,社区',
        'channels': '官网SEO,行业大会,客户推荐,应用市场',
        'customerSegments': '中小企业主(42%),技术负责人(28%),大企业采购(18%),创业团队(12%)',
        'costStructure': '研发50%,营销25%,客服15%,服务器10%',
        'revenueStreams': '订阅费75%,实施服务15%,增值功能10%',
      },
    };

    return allData[query] ?? allData['母婴']!;
  }

  Widget _buildCell(String title, String content, Color color) {
    return Container(
      margin: const EdgeInsets.all(4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1a1a3e),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(content, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}