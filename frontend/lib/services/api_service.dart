import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/analysis_result.dart';

class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  // 分析关键词，返回真实API数据
  Future<Map<String, dynamic>> analyzeKeyword(String keyword) async {
    try {
      final response = await _client
          .post(
            Uri.parse('${ApiConfig.baseUrl}/api/analyze'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'keyword': keyword}),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw ApiException('分析失败: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误，请检查后台服务是否启动: $e');
    }
  }

  // 保留旧方法名兼容
  Future<Map<String, dynamic>> analyzeComplaints(String keyword) async {
    return analyzeKeyword(keyword);
  }

  Future<Map<String, dynamic>> analyzeDeep(String keyword) async {
    try {
      final response = await _client
          .post(
            Uri.parse('${ApiConfig.baseUrl}/api/analyze/deep'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'keyword': keyword}),
          )
          .timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw ApiException('深度分析失败: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误: $e');
    }
  }

  Future<Map<String, dynamic>> generateCanvas(String keyword, String canvasType) async {
    try {
      final response = await _client
          .post(
            Uri.parse('${ApiConfig.baseUrl}/api/canvas/generate'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'keyword': keyword,
              'canvas_type': canvasType,
            }),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw ApiException('画布生成失败: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getDataSources() async {
    try {
      final response = await _client
          .get(Uri.parse('${ApiConfig.baseUrl}/api/data-sources'))
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['sources'] as List).cast<Map<String, dynamic>>();
      } else {
        throw ApiException('获取数据源失败: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误: $e');
    }
  }

  Future<Map<String, dynamic>> recommendProfitModels(String keyword) async {
    try {
      final response = await _client
          .post(
            Uri.parse('${ApiConfig.baseUrl}/api/profit-models/recommend'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'keyword': keyword}),
          )
          .timeout(ApiConfig.timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw ApiException('推荐失败: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('网络错误: $e');
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}