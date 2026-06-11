import 'package:flutter/material.dart';
import '../models/analysis_result.dart';
import '../services/mock_data_service.dart';
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

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.delayed(const Duration(milliseconds: 800));
    if (mounted) {
      setState(() {
        _result = MockDataService.getMockAnalysis(widget.query);
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('消费者洞察'),
        actions: [
          IconButton(
            icon: const Icon(Icons.data_usage),
            onPressed: () => _navigateToDataSources(),
          ),
          IconButton(
            icon: const Icon(Icons.dashboard_customize),
            onPressed: () => _navigateToLeanCanvas(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildContent(),
    );
  }

  Widget _buildContent() {
    if (_result == null) return const SizedBox.shrink();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSummaryCard(),
          const SizedBox(height: 24),
          _buildSectionTitle('抱怨分布'),
          const SizedBox(height: 12),
          _buildComplaintSection(),
          const SizedBox(height: 24),
          _buildSectionTitle('客户细分'),
          const SizedBox(height: 12),
          _buildCustomerSection(),
          const SizedBox(height: 24),
          _buildQuickActions(),
        ],
      ),
    );
  }

  Widget _buildSummaryCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.lightbulb, color: Colors.amber),
                const SizedBox(width: 8),
                const Text(
                  '分析摘要',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _result!.summary,
              style: const TextStyle(fontSize: 14, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildComplaintSection() {
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

  Widget _buildCustomerSection() {
    return Column(
      children: _result!.customerSegments.asMap().entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: CustomerSegmentCard(
            segment: entry.value,
            index: entry.key,
          ),
        );
      }).toList(),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          '快速操作',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _navigateToLeanCanvas,
                icon: const Icon(Icons.dashboard_customize),
                label: const Text('生成精益画布'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _navigateToBusinessCanvas,
                icon: const Icon(Icons.view_quilt),
                label: const Text('商业模式画布'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyan,
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
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LeanCanvasScreen(query: widget.query),
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