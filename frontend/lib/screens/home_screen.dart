import 'package:flutter/material.dart';
import '../widgets/search_box.dart';
import 'analysis_result_screen.dart';
import 'lean_canvas_screen.dart';
import 'business_canvas_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? _lastQuery;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('创业帮'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => _showHistory(context),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                '从消费者抱怨到商业模式',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                '输入关键词,AI帮你分析市场机会',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade400,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              SearchBox(
                initialValue: _lastQuery,
                onSearch: (query) {
                  setState(() => _lastQuery = query);
                  _analyzeComplaints(query);
                },
              ),
              const SizedBox(height: 32),
              const Text(
                '选择分析模式',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 1.1,
                  children: [
                    _buildModeCard(
                      context,
                      '消费者洞察',
                      '分析抱怨分布,提取客户痛点',
                      Icons.insights,
                      Colors.blue,
                      () => _lastQuery != null
                          ? _analyzeComplaints(_lastQuery!)
                          : null,
                    ),
                    _buildModeCard(
                      context,
                      '精益画布',
                      '快速验证商业假设',
                      Icons.dashboard_customize,
                      Colors.cyan,
                      () => _lastQuery != null
                          ? _generateLeanCanvas(_lastQuery!)
                          : null,
                    ),
                    _buildModeCard(
                      context,
                      '商业模式画布',
                      '系统性梳理商业模式',
                      Icons.view_quilt,
                      Colors.teal,
                      () => _lastQuery != null
                          ? _generateBusinessCanvas(_lastQuery!)
                          : null,
                    ),
                    _buildModeCard(
                      context,
                      '数据源覆盖',
                      '查看数据来源分布',
                      Icons.data_usage,
                      Colors.green,
                      () => _lastQuery != null
                          ? _showDataSources(_lastQuery!)
                          : null,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModeCard(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback? onTap,
  ) {
    return Card(
      child: InkWell(
        onTap: onTap ?? () => _showTip(context),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: color),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade400,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showTip(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('请先输入关键词进行搜索'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _analyzeComplaints(String query) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AnalysisResultScreen(query: query),
      ),
    );
  }

  void _generateLeanCanvas(String query) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LeanCanvasScreen(query: query),
      ),
    );
  }

  void _generateBusinessCanvas(String query) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => BusinessCanvasScreen(query: query),
      ),
    );
  }

  void _showDataSources(String query) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DataSourcesScreen(query: query),
      ),
    );
  }

  void _showHistory(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF2D2D2D),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '搜索历史',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              if (_lastQuery != null)
                ListTile(
                  leading: const Icon(Icons.history),
                  title: Text(_lastQuery!),
                  onTap: () {
                    Navigator.pop(context);
                    _analyzeComplaints(_lastQuery!);
                  },
                )
              else
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    '暂无搜索历史',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}