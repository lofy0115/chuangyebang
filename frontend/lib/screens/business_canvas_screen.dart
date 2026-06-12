import "package:flutter/material.dart";
import '../services/api_service.dart';

class BusinessCanvasScreen extends StatefulWidget {
  final String query;
  const BusinessCanvasScreen({super.key, required this.query});

  @override
  State<BusinessCanvasScreen> createState() => _BusinessCanvasScreenState();
}

class _BusinessCanvasScreenState extends State<BusinessCanvasScreen> {
  Map<String, String>? _canvas;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadCanvas();
  }

  Future<void> _loadCanvas() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await ApiService().generateCanvas(widget.query, 'business');
      if (mounted) {
        setState(() {
          _canvas = _parseBusinessCanvas(data);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _canvas = _getGenericCanvas(widget.query);
          _isLoading = false;
        });
      }
    }
  }

  Map<String, String> _parseBusinessCanvas(Map<String, dynamic> data) {
    return {
      'keyPartners': _toStr(data['key_partners']),
      'keyActivities': _toStr(data['key_activities']),
      'keyResources': _toStr(data['key_resources']),
      'valuePropositions': _toStr(data['value_propositions']),
      'customerRelationships': _toStr(data['customer_relationships']),
      'channels': _toStr(data['channels']),
      'customerSegments': _toStr(data['customer_segments']),
      'costStructure': _toStr(data['cost_structure']),
      'revenueStreams': _toStr(data['revenue_streams']),
    };
  }

  String _toStr(dynamic val) {
    if (val == null) return '';
    if (val is List) return val.join('\n');
    if (val is String) return val;
    return val.toString();
  }

  Map<String, String> _getGenericCanvas(String query) {
    return {
      'keyPartners': '供应商,渠道商,技术合作方',
      'keyActivities': '产品研发,用户运营,市场拓展',
      'keyResources': '技术团队,用户数据,品牌资产',
      'valuePropositions': '解决${query}行业核心痛点\n差异化价值主张\n优质用户体验',
      'customerRelationships': '在线客服,会员体系,社区运营',
      'channels': '线上平台,社交媒体,线下渠道',
      'customerSegments': '目标用户群A(核心)\n目标用户群B(扩展)',
      'costStructure': '研发成本,人力成本,营销成本,运营成本',
      'revenueStreams': '产品/服务收入,会员收入,增值服务',
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('📋 商业模式画布 - ${widget.query}')),
      body: Container(
        color: const Color(0xFF0f0f23),
        child: _isLoading
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.white),
                    SizedBox(height: 16),
                    Text('正在生成商业模式画布...',
                        style: TextStyle(color: Colors.white70)),
                  ],
                ),
              )
            : _canvas == null
                ? const Center(
                    child: Text('生成失败',
                        style: TextStyle(color: Colors.red)),
                  )
                : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        Row(children: [
                          Expanded(
                              child: _buildCell(
                                  '关键合作伙伴',
                                  _canvas!['keyPartners']!,
                                  Colors.blue)),
                          Expanded(
                              child: _buildCell(
                                  '关键活动',
                                  _canvas!['keyActivities']!,
                                  Colors.teal)),
                          Expanded(
                              child: _buildCell(
                                  '核心资源',
                                  _canvas!['keyResources']!,
                                  Colors.indigo)),
                        ]),
                        Row(children: [
                          Expanded(
                              child: _buildCell(
                                  '价值主张',
                                  _canvas!['valuePropositions']!,
                                  Colors.purple)),
                          Expanded(
                              child: _buildCell(
                                  '客户关系',
                                  _canvas!['customerRelationships']!,
                                  Colors.pink)),
                          Expanded(
                              child: _buildCell(
                                  '渠道', _canvas!['channels']!, Colors.cyan)),
                        ]),
                        Row(children: [
                          Expanded(
                              child: _buildCell(
                                  '客户细分',
                                  _canvas!['customerSegments']!,
                                  Colors.orange)),
                          const Expanded(child: SizedBox()),
                          const Expanded(child: SizedBox()),
                        ]),
                        const Divider(color: Colors.white24),
                        Row(children: [
                          Expanded(
                              child: _buildCell(
                                  '成本结构',
                                  _canvas!['costStructure']!,
                                  Colors.grey)),
                          Expanded(
                              child: _buildCell(
                                  '收入来源',
                                  _canvas!['revenueStreams']!,
                                  Colors.green)),
                          const Expanded(child: SizedBox()),
                        ]),
                        const SizedBox(height: 24),
                        _buildLegend(),
                      ],
                    ),
                  ),
      ),
    );
  }

  Widget _buildCell(String title, String content, Color color) {
    if (content.isEmpty) {
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
            Text(title,
                style: TextStyle(
                    color: color, fontSize: 11, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            const Text('待填充', style: TextStyle(color: Colors.white38)),
          ],
        ),
      );
    }

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
          Text(title,
              style: TextStyle(
                  color: color, fontSize: 11, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(content,
              style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF252550),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '📌 画布使用说明',
            style: TextStyle(
                color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
          ),
          SizedBox(height: 8),
          Text(
            '• 左列：成本端（合作伙伴/活动/资源）\n'
            '• 中列：价值主张和客户关系\n'
            '• 右列：收入端（渠道/客户细分）\n'
            '• 底行：成本结构和收入来源\n'
            '• 根据你的业务实际情况调整各模块内容',
            style: TextStyle(color: Colors.white60, fontSize: 11, height: 1.6),
          ),
        ],
      ),
    );
  }
}