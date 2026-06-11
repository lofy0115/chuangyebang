class LeanCanvas {
  final String problem;
  final String solution;
  final String uniqueValue;
  final String unfairAdvantage;
  final String keyMetrics;
  final String channels;
  final String costStructure;
  final String revenueStreams;

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

  factory LeanCanvas.fromJson(Map<String, dynamic> json) {
    return LeanCanvas(
      problem: json['problem'] ?? '',
      solution: json['solution'] ?? '',
      uniqueValue: json['unique_value'] ?? '',
      unfairAdvantage: json['unfair_advantage'] ?? '',
      keyMetrics: json['key_metrics'] ?? '',
      channels: json['channels'] ?? '',
      costStructure: json['cost_structure'] ?? '',
      revenueStreams: json['revenue_streams'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
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
}