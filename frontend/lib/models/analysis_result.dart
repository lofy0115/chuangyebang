import 'complaint_type.dart';
import 'customer_segment.dart';
import 'business_canvas.dart';
import 'lean_canvas.dart';

class AnalysisResult {
  final String id;
  final String searchQuery;
  final DateTime timestamp;
  final List<ComplaintType> complaintTypes;
  final List<CustomerSegment> customerSegments;
  final BusinessCanvas? businessCanvas;
  final LeanCanvas? leanCanvas;
  final Map<String, int> dataSourceCoverage;
  final String summary;

  AnalysisResult({
    required this.id,
    required this.searchQuery,
    required this.timestamp,
    this.complaintTypes = const [],
    this.customerSegments = const [],
    this.businessCanvas,
    this.leanCanvas,
    this.dataSourceCoverage = const {},
    this.summary = '',
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      id: json['id'] ?? '',
      searchQuery: json['search_query'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      complaintTypes: (json['complaint_types'] as List?)
              ?.map((e) => ComplaintType.fromJson(e))
              .toList() ??
          [],
      customerSegments: (json['customer_segments'] as List?)
              ?.map((e) => CustomerSegment.fromJson(e))
              .toList() ??
          [],
      businessCanvas: json['business_canvas'] != null
          ? BusinessCanvas.fromJson(json['business_canvas'])
          : null,
      leanCanvas: json['lean_canvas'] != null
          ? LeanCanvas.fromJson(json['lean_canvas'])
          : null,
      dataSourceCoverage:
          Map<String, int>.from(json['data_source_coverage'] ?? {}),
      summary: json['summary'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'search_query': searchQuery,
      'timestamp': timestamp.toIso8601String(),
      'complaint_types': complaintTypes.map((e) => e.toJson()).toList(),
      'customer_segments': customerSegments.map((e) => e.toJson()).toList(),
      'business_canvas': businessCanvas?.toJson(),
      'lean_canvas': leanCanvas?.toJson(),
      'data_source_coverage': dataSourceCoverage,
      'summary': summary,
    };
  }
}