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
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      count: json['count'] ?? 0,
      percentage: (json['percentage'] ?? 0).toDouble(),
      relatedProducts: List<String>.from(json['related_products'] ?? []),
      suggestions: List<String>.from(json['suggestions'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'count': count,
      'percentage': percentage,
      'related_products': relatedProducts,
      'suggestions': suggestions,
    };
  }
}