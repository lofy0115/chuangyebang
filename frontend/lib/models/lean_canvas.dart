class LeanCanvas {
  final List<String> problem;
  final List<String> solution;
  final String uniqueValue;
  final List<String> unfairAdvantage;
  final List<String> keyMetrics;
  final List<String> channels;
  final String costStructure;
  final List<String> revenueStreams;

  LeanCanvas({
    required this.problem,
    required this.solution,
    required this.uniqueValue,
    required this.unfairAdvantage,
    required this.keyMetrics,
    required this.channels,
    required this.costStructure,
    required this.revenueStreams,
  });

  factory LeanCanvas.fromApiJson(Map<String, dynamic> json) {
    return LeanCanvas(
      problem: _toStringList(json['problem']),
      solution: _toStringList(json['solution']),
      uniqueValue: json['unique_value'] ?? '',
      unfairAdvantage: _toStringList(json['unfair_advantage']),
      keyMetrics: _toStringList(json['key_metrics']),
      channels: _toStringList(json['channels']),
      costStructure: json['cost_structure'] ?? '',
      revenueStreams: _toStringList(json['revenue_streams']),
    );
  }

  static List<String> _toStringList(dynamic value) {
    if (value == null) return [];
    if (value is List) return value.map((e) => e.toString()).toList();
    if (value is String) return value.split('\n').where((s) => s.trim().isNotEmpty).toList();
    return [];
  }

  Map<String, dynamic> toJson() => {
        'problem': problem,
        'solution': solution,
        'unique_value': uniqueValue,
        'unfair_advantage': unfairAdvantage,
        'key_metrics': keyMetrics,
        'channels': channels,
        'cost_structure': costStructure,
        'revenue_streams': revenueStreams,
      };
}