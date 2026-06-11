import "package:flutter/material.dart";
import '../services/mock_data_service.dart';

class LeanCanvasScreen extends StatelessWidget {
  final String query;
  const LeanCanvasScreen({super.key, required this.query});

  @override
  Widget build(BuildContext context) {
    final result = MockDataService.getMockLeanCanvas(query);
    final canvas = result.leanCanvas;

    return Scaffold(
      appBar: AppBar(title: Text('🎯 精益画布 - $query')),
      body: Container(
        color: const Color(0xFF0f0f23),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              _buildCell('问题', canvas?.problem ?? '', Colors.red.shade400),
              _buildCell('解决方案', canvas?.solution ?? '', Colors.blue.shade400),
              _buildCell('独特价值主张', canvas?.uniqueValue ?? '', Colors.purple.shade400),
              _buildCell('门槛优势', canvas?.unfairAdvantage ?? '', Colors.orange.shade400),
              _buildCell('关键指标', canvas?.keyMetrics ?? '', Colors.teal.shade400),
              _buildCell('渠道', canvas?.channels ?? '', Colors.cyan.shade400),
              _buildCell('成本结构', canvas?.costStructure ?? '', Colors.grey.shade400),
              _buildCell('收入来源', canvas?.revenueStreams ?? '', Colors.green.shade400),
            ],
          ),
        ),
      ),
    );
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