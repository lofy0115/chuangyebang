import 'package:flutter/material.dart';
import '../models/analysis_result.dart';
import '../models/pain_point.dart';
import '../services/api_service.dart';
import '../widgets/complaint_chart.dart';
import '../widgets/customer_segment_card.dart';
import 'data_sources_screen.dart';
import 'lean_canvas_screen.dart';
import 'business_canvas_screen.dart';

class AnalysisResultScreen extends StatefulWidget {
  final String query;

  const AnalysisResultScreen({super.key, required this.query});

  @override
  State<AnalysisResultScreen> createState() => _AnalysisResultScreenState();
}

class _AnalysisResultScreenState extends State<AnalysisResultScreen> {
  AnalysisResult? _result;
  bool _isLoading = true;
  String? _error;
  Set<int> _selectedPainPointIndices = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await ApiService.analyzeKeyword(widget.query);
      if (mounted) {
        setState(() {
          _result = AnalysisResult.fromApiJson(data, widget.query);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.query} - 消费者洞察'),
        actions: [
          IconButton(
            icon: const Icon(Icons.data_usage),
            onPressed: () => _navigateToDataSources(),
            tooltip: '数据来源',
          ),
          IconButton(
            icon: const Icon(Icons.dashboard_customize),
            onPressed: _result != null ? _navigateToLeanCanvas : null,
            tooltip: '生成精益画布',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('正在分析消费者反馈...'),
            SizedBox(height: 8),
            Text('爬取各平台抱怨数据，智能分类中',
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text('分析失败', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh),
                label: const Text('重试'),
              ),
            ],
          ),
        ),
      );
    }

    if (_result == null) return const SizedBox.shrink();

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSummaryCard(),
            const SizedBox(height: 24),
            _buildSectionTitle('抱怨智能分类分布'),
            const SizedBox(height: 8),
            Text(
              '基于 ${_result!.totalRecords} 条真实消费者反馈智能分析',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            const SizedBox(height: 12),
            _buildComplaintSection(),
            const SizedBox(height: 24),
            _buildPainPointSection(),
            const SizedBox(height: 24),
            _buildCustomerSection(),
            const SizedBox(height: 24),
            _buildQuickActions(),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard() {
    final sentimentIcon = _result!.avgSentiment > 0
        ? Icons.sentiment_satisfied
        : _result!.avgSentiment < 0
            ? Icons.sentiment_dissatisfied
            : Icons.sentiment_neutral;
    final sentimentColor = _result!.avgSentiment > 0
        ? Colors.green
        : _result!.avgSentiment < 0
            ? Colors.red
            : Colors.grey;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb, color: Colors.amber[700]),
                const SizedBox(width: 8),
                Text(
                  '${_result!.industry} 行业洞察摘要',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _result!.summary,
              style: const TextStyle(fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(sentimentIcon, color: sentimentColor, size: 20),
                const SizedBox(width: 6),
                Text(
                  _result!.avgSentiment > 0
                      ? '情感倾向: 正面'
                      : _result!.avgSentiment < 0
                          ? '情感倾向: 负面'
                          : '情感倾向: 中性',
                  style: TextStyle(color: sentimentColor, fontSize: 13),
                ),
                const SizedBox(width: 24),
                const Icon(Icons.article_outlined, size: 20, color: Colors.grey),
                const SizedBox(width: 6),
                Text(
                  '样本: ${_result!.totalRecords} 条',
                  style: const TextStyle(color: Colors.grey, fontSize: 13),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
    );
  }

  Widget _buildComplaintSection() {
    if (_result!.complaintTypes.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('暂无抱怨数据'),
        ),
      );
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          flex: 2,
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: ComplaintChart(complaints: _result!.complaintTypes),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: ComplaintLegend(complaints: _result!.complaintTypes),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPainPointSection() {
    final painPoints = _result!.topValueNeeds;
    if (painPoints.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _buildSectionTitle('🎯 高价值痛点 (可多选)'),
            const Spacer(),
            Text(
              '已选 ${_selectedPainPointIndices.length}/${painPoints.length}',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          '选择你要重点解决的痛点，画布将基于你的选择量身定制',
          style: TextStyle(color: Colors.grey, fontSize: 12),
        ),
        const SizedBox(height: 12),
        ...painPoints.asMap().entries.map((entry) {
          final index = entry.key;
          final pp = entry.value;
          final isSelected = _selectedPainPointIndices.contains(index);
          return Card(
            color: isSelected ? Colors.blue[50] : null,
            child: InkWell(
              onTap: () => _togglePainPoint(index),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Checkbox(
                      value: isSelected,
                      onChanged: (_) => _togglePainPoint(index),
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  pp.need,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: _getPriorityColor(pp.priority),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  '优先级 ${pp.priority}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '痛点: ${pp.pain}',
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 12,
                            ),
                          ),
                          if (pp.sourceComplaints > 0) ...[
                            const SizedBox(height: 2),
                            Text(
                              '来源: ${pp.sourceComplaints} 条相关抱怨',
                              style: const TextStyle(
                                color: Colors.grey,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Color _getPriorityColor(int priority) {
    if (priority >= 90) return Colors.red;
    if (priority >= 80) return Colors.orange;
    if (priority >= 70) return Colors.amber[700]!;
    return Colors.blue;
  }

  void _togglePainPoint(int index) {
    setState(() {
      if (_selectedPainPointIndices.contains(index)) {
        _selectedPainPointIndices.remove(index);
      } else {
        _selectedPainPointIndices.add(index);
      }
    });
  }

  Widget _buildCustomerSection() {
    final segments = _result!.customerSegments;
    if (segments.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('👥 客户细分画像'),
        const SizedBox(height: 12),
        ...segments.asMap().entries.map((entry) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: CustomerSegmentCard(
              segment: entry.value,
              index: entry.key,
            ),
          );
        }),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          '🚀 快速操作',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _result != null ? _navigateToLeanCanvas : null,
                icon: const Icon(Icons.dashboard_customize),
                label: Text(
                  _selectedPainPointIndices.isEmpty
                      ? '生成精益画布'
                      : '基于 ${_selectedPainPointIndices.length} 个痛点生成画布',
                ),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _result != null ? _navigateToBusinessCanvas : null,
                icon: const Icon(Icons.view_quilt),
                label: const Text('商业模式画布'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyan,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  void _navigateToDataSources() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DataSourcesScreen(query: widget.query),
      ),
    );
  }

  void _navigateToLeanCanvas() {
    final selectedPainPoints = _selectedPainPointIndices.isEmpty
        ? _result!.topValueNeeds
        : _selectedPainPointIndices
            .map((i) => _result!.topValueNeeds[i])
            .toList();

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LeanCanvasScreen(
          query: widget.query,
          painPoints: selectedPainPoints,
        ),
      ),
    );
  }

  void _navigateToBusinessCanvas() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => BusinessCanvasScreen(query: widget.query),
      ),
    );
  }
}

class ComplaintLegend extends StatelessWidget {
  final List<ComplaintType> complaints;

  const ComplaintLegend({super.key, required this.complaints});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: complaints.map((c) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: _getColorForType(c.name),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  '${c.name} ${c.percentage.toStringAsFixed(1)}%',
                  style: const TextStyle(fontSize: 11),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Color _getColorForType(String type) {
    switch (type) {
      case '性能问题':
        return Colors.blue;
      case '价格问题':
        return Colors.green;
      case '功能缺失':
        return Colors.purple;
      case '服务体验':
        return Colors.orange;
      case '质量缺陷':
        return Colors.red;
      case '安全隐患':
        return Colors.deepOrange;
      case '交付问题':
        return Colors.teal;
      default:
        return Colors.grey;
    }
  }
}