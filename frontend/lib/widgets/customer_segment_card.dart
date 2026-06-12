import 'package:flutter/material.dart';
import '../models/customer_segment.dart';

class CustomerSegmentCard extends StatelessWidget {
  final CustomerSegment segment;
  final int index;

  const CustomerSegmentCard({
    super.key,
    required this.segment,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _getColor(index).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    segment.name,
                    style: TextStyle(
                      color: _getColor(index),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (segment.size > 0) ...[
                  const Spacer(),
                  Text(
                    '${(segment.size / 1000000).toStringAsFixed(1)}M用户',
                    style: TextStyle(
                      color: Colors.grey.shade400,
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
            if (segment.description.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                segment.description,
                style: const TextStyle(fontSize: 14),
              ),
            ],
            if (segment.spending > 0) ...[
              const SizedBox(height: 8),
              _buildInfoRow('月均消费', '¥${segment.spending.toStringAsFixed(0)}'),
            ],
            if (segment.needs.isNotEmpty) ...[
              const SizedBox(height: 8),
              _buildTags('需求', segment.needs),
            ],
            if (segment.painPoints.isNotEmpty) ...[
              const SizedBox(height: 8),
              _buildTags('痛点', segment.painPoints),
            ],
            if (segment.behaviorPattern.isNotEmpty) ...[
              const SizedBox(height: 8),
              _buildInfoRow('行为特征', segment.behaviorPattern),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 12,
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontSize: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildTags(String label, List<String> tags) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: tags.map((tag) {
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.grey.shade800,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                tag,
                style: const TextStyle(fontSize: 11),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Color _getColor(int index) {
    final colors = [
      Colors.blue,
      Colors.cyan,
      Colors.teal,
      Colors.green,
      Colors.orange,
    ];
    return colors[index % colors.length];
  }
}