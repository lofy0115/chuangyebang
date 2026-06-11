import 'package:flutter/material.dart';

class CanvasCell extends StatelessWidget {
  final String title;
  final String content;
  final Color color;

  const CanvasCell({
    super.key,
    required this.title,
    required this.content,
    this.color = const Color(0xFF2D2D2D),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.grey.shade800,
          width: 1,
        ),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              color: Colors.blue.shade300,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: SingleChildScrollView(
              child: Text(
                content.isEmpty ? '-' : content,
                style: const TextStyle(
                  fontSize: 13,
                  height: 1.4,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}