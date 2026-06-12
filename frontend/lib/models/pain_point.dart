class PainPoint {
  final String need;
  final String pain;
  final int priority;
  final int sourceComplaints;

  PainPoint({
    required this.need,
    required this.pain,
    required this.priority,
    this.sourceComplaints = 0,
  });

  factory PainPoint.fromJson(Map<String, dynamic> json) {
    return PainPoint(
      need: json['need'] ?? '',
      pain: json['pain'] ?? '',
      priority: json['priority'] ?? 0,
      sourceComplaints: json['source_complaints'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
        'need': need,
        'pain': pain,
        'priority': priority,
        'source_complaints': sourceComplaints,
      };
}