import 'pain_point.dart';
import 'customer_segment.dart';

class ComplaintType {
  final String id;
  final String name;
  final String description;
  final int count;
  final double percentage;
  final List<String> relatedProducts;
  final List<String> suggestions;

  ComplaintType({
    required this.id,
    required this.name,
    required this.description,
    required this.count,
    required this.percentage,
    this.relatedProducts = const [],
    this.suggestions = const [],
  });

  factory ComplaintType.fromJson(Map<String, dynamic> json) {
    return ComplaintType(
      id: json['id'] ?? json['type'] ?? '',
      name: json['name'] ?? json['type'] ?? '',
      description: json['description'] ?? '',
      count: json['count'] ?? 0,
      percentage: (json['percentage'] ?? 0).toDouble(),
      relatedProducts: List<String>.from(json['related_products'] ?? []),
      suggestions: List<String>.from(json['suggestions'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'description': description,
        'count': count,
        'percentage': percentage,
        'related_products': relatedProducts,
        'suggestions': suggestions,
      };
}

class AnalysisResult {
  final String id;
  final String searchQuery;
  final DateTime timestamp;
  final String industry;
  final int totalRecords;
  final double avgSentiment;
  final List<ComplaintType> complaintTypes;
  final List<PainPoint> topValueNeeds;
  final List<CustomerSegment> customerSegments;
  final String summary;

  AnalysisResult({
    required this.id,
    required this.searchQuery,
    required this.timestamp,
    required this.industry,
    required this.totalRecords,
    this.avgSentiment = 0,
    this.complaintTypes = const [],
    this.topValueNeeds = const [],
    this.customerSegments = const [],
    this.summary = '',
  });

  factory AnalysisResult.fromApiJson(Map<String, dynamic> json, String query) {
    final complaintDist = json['complaint_distribution'] as List? ?? [];
    final topNeeds = json['top_value_needs'] as List? ?? [];
    final segments = json['customer_segments'] as List? ?? [];

    return AnalysisResult(
      id: 'real_${DateTime.now().millisecondsSinceEpoch}',
      searchQuery: query,
      timestamp: DateTime.now(),
      industry: json['industry'] ?? query,
      totalRecords: json['total_records'] ?? 0,
      avgSentiment: (json['avg_sentiment'] ?? 0).toDouble(),
      complaintTypes: complaintDist
          .map((e) => ComplaintType(
                id: e['type'] ?? '',
                name: e['type'] ?? '',
                description: '',
                count: e['count'] ?? 0,
                percentage: (e['percentage'] ?? 0).toDouble(),
              ))
          .toList(),
      topValueNeeds: topNeeds.map((e) => PainPoint.fromJson(e)).toList(),
      customerSegments:
          segments.map((e) => CustomerSegment.fromApiJson(e)).toList(),
      summary: _generateSummary(
        json['industry'] ?? query,
        complaintDist,
        json['avg_sentiment'] ?? 0,
      ),
    );
  }

  static String _generateSummary(
      String industry, List<dynamic> dist, double sentiment) {
    if (dist.isEmpty) return '暂无数据';
    final top = dist.first;
    final topType = top['type'] ?? '其他';
    final topPct = top['percentage'] ?? 0;
    final sentimentText = sentiment > 0
        ? '整体口碑偏正面'
        : sentiment < 0
            ? '整体口碑偏负面'
            : '整体口碑中性';
    return '$industry行业消费者反馈$sentimentText，$topType占比最高(${topPct}%)，是核心改进方向。';
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'search_query': searchQuery,
        'timestamp': timestamp.toIso8601String(),
        'industry': industry,
        'total_records': totalRecords,
        'avg_sentiment': avgSentiment,
        'complaint_types': complaintTypes.map((e) => e.toJson()).toList(),
        'top_value_needs': topValueNeeds.map((e) => e.toJson()).toList(),
        'customer_segments': customerSegments.map((e) => e.toJson()).toList(),
        'summary': summary,
      };
}