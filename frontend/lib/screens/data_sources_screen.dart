import "package:flutter/material.dart";
import '../services/api_service.dart';

class DataSourcesScreen extends StatefulWidget {
  final String query;
  const DataSourcesScreen({super.key, required this.query});

  @override
  State<DataSourcesScreen> createState() => _DataSourcesScreenState();
}

class _DataSourcesScreenState extends State<DataSourcesScreen> {
  List<Map<String, dynamic>> _sources = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSources();
  }

  Future<void> _loadSources() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await ApiService().getDataSources();
      if (mounted) {
        setState(() {
          _sources = data;
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
      appBar: AppBar(title: Text('📡 数据源覆盖 - ${widget.query}')),
      body: Container(
        color: const Color(0xFF0f0f23),
        padding: const EdgeInsets.all(16),
        child: _isLoading
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: Colors.white),
                    SizedBox(height: 16),
                    Text('正在获取数据源列表...',
                        style: TextStyle(color: Colors.white70)),
                  ],
                ),
              )
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('加载失败: $_error',
                            style: const TextStyle(color: Colors.red)),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadSources,
                          child: const Text('重试'),
                        ),
                      ],
                    ),
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "共 ${_sources.length} 个数据源",
                        style:
                            const TextStyle(color: Colors.white70, fontSize: 14),
                      ),
                      const SizedBox(height: 16),
                      Expanded(
                        child: GridView.count(
                          crossAxisCount: 2,
                          mainAxisSpacing: 12,
                          crossAxisSpacing: 12,
                          childAspectRatio: 1.5,
                          children: _sources.map<Widget>((e) {
                            final name = e['name'] ?? e['id'] ?? '';
                            final type = e['type'] ?? 'unknown';
                            return Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFF1a1a3e),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    name,
                                    style: const TextStyle(
                                        color: Colors.white70, fontSize: 13),
                                  ),
                                  const SizedBox(height: 4),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: _getTypeColor(type),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: Text(
                                      type,
                                      style: const TextStyle(
                                          color: Colors.white, fontSize: 10),
                                    ),
                                  ),
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
                          "权重配置：投诉平台 > 电商平台 > 社交媒体 > 论坛社区\n确保数据客观性：多源交叉验证",
                          style: TextStyle(color: Colors.white60, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
      ),
    );
  }

  Color _getTypeColor(String type) {
    switch (type) {
      case 'domestic_cn':
        return Colors.green;
      case 'complaint':
        return Colors.red;
      case 'social':
        return Colors.blue;
      case 'forum':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}