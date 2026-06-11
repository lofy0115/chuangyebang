class BusinessCanvas {
  final String keyPartners;
  final String keyActivities;
  final String keyResources;
  final String valuePropositions;
  final String customerRelationships;
  final String channels;
  final String customerSegments;
  final String costStructure;
  final String revenueStreams;

  BusinessCanvas({
    required this.keyPartners,
    required this.keyActivities,
    required this.keyResources,
    required this.valuePropositions,
    required this.customerRelationships,
    required this.channels,
    required this.customerSegments,
    required this.costStructure,
    required this.revenueStreams,
  });

  factory BusinessCanvas.fromJson(Map<String, dynamic> json) {
    return BusinessCanvas(
      keyPartners: json['key_partners'] ?? '',
      keyActivities: json['key_activities'] ?? '',
      keyResources: json['key_resources'] ?? '',
      valuePropositions: json['value_propositions'] ?? '',
      customerRelationships: json['customer_relationships'] ?? '',
      channels: json['channels'] ?? '',
      customerSegments: json['customer_segments'] ?? '',
      costStructure: json['cost_structure'] ?? '',
      revenueStreams: json['revenue_streams'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'key_partners': keyPartners,
      'key_activities': keyActivities,
      'key_resources': keyResources,
      'value_propositions': valuePropositions,
      'customer_relationships': customerRelationships,
      'channels': channels,
      'customer_segments': customerSegments,
      'cost_structure': costStructure,
      'revenue_streams': revenueStreams,
    };
  }

  List<Map<String, String>> toCells() {
    return [
      {'title': '关键合作', 'content': keyPartners},
      {'title': '关键活动', 'content': keyActivities},
      {'title': '关键资源', 'content': keyResources},
      {'title': '价值主张', 'content': valuePropositions},
      {'title': '客户关系', 'content': customerRelationships},
      {'title': '渠道', 'content': channels},
      {'title': '客户细分', 'content': customerSegments},
      {'title': '成本结构', 'content': costStructure},
      {'title': '收入来源', 'content': revenueStreams},
    ];
  }
}