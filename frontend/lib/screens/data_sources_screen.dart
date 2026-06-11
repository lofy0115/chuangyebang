import "package:flutter/material.dart";
import '../services/mock_data_service.dart';

class DataSourcesScreen extends StatelessWidget {
  final String query;
  const DataSourcesScreen({super.key, required this.query});

  @override
  Widget build(BuildContext context) {
    final result = MockDataService.getMockAnalysis(query);
    final coverage = result.dataSourceCoverage;

    return Scaffold(
      appBar: AppBar(title: Text('📡 数据源覆盖 - $query')),
      body: Container(
        color: const Color(0xFF0f0f23),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("共 ${coverage.length} 个数据源", style: const TextStyle(color: Colors.white70, fontSize: 14)),
            const SizedBox(height: 16),
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.5,
                children: coverage.entries.map<Widget>((e) {
                  return Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1a1a3e),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(e.key, style: const TextStyle(color: Colors.white70, fontSize: 13)),
                        const SizedBox(height: 4),
                        Text('${e.value}%', style: const TextStyle(color: Color(0xFF00d4ff), fontSize: 24, fontWeight: FontWeight.bold)),
                        const Text('覆盖率', style: TextStyle(color: Colors.white38, fontSize: 11)),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF252550),
                borderRadius: BorderRadius.circular(10),
              ),
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