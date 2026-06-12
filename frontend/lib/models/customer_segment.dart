class CustomerSegment {
  final String id;
  final String name;
  final String description;
  final int size;
  final double spending;
  final List<String> painPoints;
  final List<String> needs;
  final String behaviorPattern;

  CustomerSegment({
    required this.id,
    required this.name,
    required this.description,
    required this.size,
    required this.spending,
    this.painPoints = const [],
    this.needs = const [],
    this.behaviorPattern = '',
  });

  // 从API新格式解析（segment字段）
  factory CustomerSegment.fromApiJson(Map<String, dynamic> json) {
    return CustomerSegment(
      id: json['id'] ?? json['segment'] ?? '',
      name: json['name'] ?? json['segment'] ?? '',
      description: json['description'] ?? '',
      size: json['size'] ?? 0,
      spending: (json['spending'] ?? 0).toDouble(),
      painPoints: List<String>.from(json['pain_points'] ?? []),
      needs: List<String>.from(json['needs'] ?? []),
      behaviorPattern: json['behavior_pattern'] ?? '',
    );
  }

  factory CustomerSegment.fromJson(Map<String, dynamic> json) {
    return CustomerSegment(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      size: json['size'] ?? 0,
      spending: (json['spending'] ?? 0).toDouble(),
      painPoints: List<String>.from(json['pain_points'] ?? []),
      needs: List<String>.from(json['needs'] ?? []),
      behaviorPattern: json['behavior_pattern'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'size': size,
      'spending': spending,
      'pain_points': painPoints,
      'needs': needs,
      'behavior_pattern': behaviorPattern,
    };
  }
}