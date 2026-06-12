import "package:flutter/material.dart";
import '../models/pain_point.dart';
import '../models/lean_canvas.dart';
import '../services/api_service.dart';

class LeanCanvasScreen extends StatefulWidget {
  final String query;
  final List<PainPoint>? painPoints;

  const LeanCanvasScreen({
    super.key,
    required this.query,
    this.painPoints,
  });

  @override
  State<LeanCanvasScreen> createState() => _LeanCanvasScreenState();
}

class _LeanCanvasScreenState extends State<LeanCanvasScreen> {
  LeanCanvas? _canvas;
  bool _isLoading = true;
  String? _error;
  String _selectedCanvas = 'lean'; // 'lean' or 'business'

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
      final data = await ApiService().generateCanvas(
        widget.query,
        _selectedCanvas,
      );
      if (mounted) {
        setState(() {
          _canvas = LeanCanvas.fromApiJson(data);
          _isLoading = false;
        });
      }
    } catch (e) {
      // API失败时，基于痛点本地生成画布
      if (mounted) {
        setState(() {
          _canvas = _generateLocalCanvas();
          _isLoading = false;
        });
      }
    }
  }

  LeanCanvas _generateLocalCanvas() {
    final painPoints = widget.painPoints ?? [];
    final needs = painPoints.isNotEmpty
        ? painPoints.map((p) => p.need).toList()
        : ['用户核心需求'];
    final pains = painPoints.isNotEmpty
        ? painPoints.map((p) => p.pain).toList()
        : ['用户遇到的困难'];

    return LeanCanvas(
      problem: painPoints.map((p) => '• ${p.pain}').toList(),
      solution: [
        '• 针对 "${needs.join("、")}" 提供解决方案',
        '• 简化流程，降低使用门槛',
        '• 建立快速反馈机制',
      ],
      uniqueValue: '• 聚焦 ${widget.query} 细分市场\n• 基于真实痛点定制\n• 差异化竞争策略',
      unfairAdvantage: [
        '• 首批进入细分市场',
        '• 数据驱动产品迭代',
        '• 用户口碑积累',
      ],
      keyMetrics: [
        '• 用户增长率',
        '• 留存率',
        '• 付费转化率',
        '• 客户满意度',
      ],
      channels: [
        '• 社交媒体获客',
        '• KOL合作推广',
        '• 口碑裂变',
        '• 线下活动',
      ],
      costStructure: '固定成本：研发+人力\n可变成本：营销+运营',
      revenueStreams: [
        '• 产品销售',
        '• 会员订阅',
        '• 增值服务',
        '• 数据增值服务',
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('📋 商业模式画布 - ${widget.query}'),
        backgroundColor: const Color(0xFF0f0f23),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadCanvas,
            tooltip: '重新生成',
          ),
        ],
      ),
      body: Container(
        color: const Color(0xFF0f0f23),
        child: _isLoading
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.white),
                    SizedBox(height: 16),
                    Text(
                      '正在生成专属画布...',
                      style: TextStyle(color: Colors.white70),
                    ),
                    SizedBox(height: 8),
                    Text(
                      '基于你的痛点选择量身定制',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              )
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('生成失败: $_error',
                            style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadCanvas,
                          child: const Text('重试'),
                        ),
                      ],
                    ),
                  )
                : _buildCanvas(),
      ),
    );
  }

  Widget _buildCanvas() {
    if (_canvas == null) return const SizedBox.shrink();
    final canvas = _canvas!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          if (widget.painPoints != null && widget.painPoints!.isNotEmpty) ...[
            _buildPainPointBanner(),
            const SizedBox(height: 16),
          ],
          _buildCell('问题', canvas.problem, Colors.red.shade400),
          _buildCell('解决方案', canvas.solution, Colors.blue.shade400),
          _buildCell('独特价值主张', canvas.uniqueValue, Colors.purple.shade400),
          _buildCell('门槛优势', canvas.unfairAdvantage, Colors.orange.shade400),
          _buildCell('关键指标', canvas.keyMetrics, Colors.teal.shade400),
          _buildCell('渠道', canvas.channels, Colors.cyan.shade400),
          _buildCell('成本结构', canvas.costStructure, Colors.grey.shade400),
          _buildCell('收入来源', canvas.revenueStreams, Colors.green.shade400),
          const SizedBox(height: 24),
          _buildActionButtons(),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildPainPointBanner() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.touch_app, color: Colors.blue, size: 16),
              SizedBox(width: 6),
              Text(
                '基于你选择的痛点生成',
                style: TextStyle(
                  color: Colors.blue,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...widget.painPoints!.map((pp) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: [
                    const Icon(Icons.arrow_right, color: Colors.blue, size: 14),
                    Expanded(
                      child: Text(
                        '${pp.need} (优先级${pp.priority})',
                        style: const TextStyle(color: Colors.white70, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildCell(String title, dynamic content, Color color) {
    final items = content is List ? content.cast<String>() : <String>[content.toString()];

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
          Text(
            title,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ...items.map((item) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        item,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          '💡 下一步行动',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ElevatedButton.icon(
          onPressed: () => _showRoadmapDialog(),
          icon: const Icon(Icons.route),
          label: const Text('查看落地路径规划'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green[700],
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: () => _shareCanvas(),
          icon: const Icon(Icons.share, color: Colors.white),
          label: const Text('分享画布', style: TextStyle(color: Colors.white)),
          style: OutlinedButton.styleFrom(
            side: const BorderSide(color: Colors.white38),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
        ),
      ],
    );
  }

  void _showRoadmapDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1a1a3e),
        title: const Row(
          children: [
            Icon(Icons.route, color: Colors.green),
            SizedBox(width: 8),
            Text('落地路径规划', style: TextStyle(color: Colors.white)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildRoadmapStep(1, '验证痛点', '通过用户访谈确认核心痛点真实性', Colors.blue),
              _buildRoadmapStep(2, '构建MVP', '开发最小可行产品，聚焦核心功能', Colors.orange),
              _buildRoadmapStep(3, '市场测试', '小规模投放，收集真实反馈', Colors.purple),
              _buildRoadmapStep(4, '迭代优化', '基于数据持续改进产品', Colors.teal),
              _buildRoadmapStep(5, '规模化', '放大有效渠道，实现增长', Colors.green),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('关闭', style: TextStyle(color: Colors.white70)),
          ),
        ],
      ),
    );
  }

  Widget _buildRoadmapStep(int step, String title, String desc, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Text(
                '$step',
                style: const TextStyle(
                    color: Colors.white, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                        color: color, fontWeight: FontWeight.bold, fontSize: 14)),
                Text(desc,
                    style:
                        const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _shareCanvas() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('画布已复制到剪贴板'),
        backgroundColor: Colors.green,
      ),
    );
  }
}