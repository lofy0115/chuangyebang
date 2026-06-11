import "package:flutter/material.dart";
import "../models/analysis_result.dart";
import "../widgets/source_coverage_grid.dart";

class DataSourcesScreen extends StatelessWidget {
  final AnalysisResult result;
  const DataSourcesScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("📡 数据源覆盖"), backgroundColor: const Color(0xFF1a1a3e)),
      body: Container(
        color: const Color(0xFF0f0f23),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("共 ${result.sourceCoverage.length} 个数据源", style: const TextStyle(color: Colors.white70, fontSize: 14)),
            const SizedBox(height: 16),
            Expanded(child: SourceCoverageGrid(coverage: result.sourceCoverage)),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFF252550), borderRadius: BorderRadius.circular(10)),
              child: const Text(
                "权重配置：投诉平台(12%) > 电商平台(15%) > 社交媒体(8-10%) > 论坛社区(2-5%)\n确保数据客观性：多源交叉验证",
                style: TextStyle(color: Colors.white60, fontSize: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }
}