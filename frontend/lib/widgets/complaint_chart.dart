import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/complaint_type.dart';

class ComplaintChart extends StatelessWidget {
  final List<ComplaintType> complaints;

  const ComplaintChart({super.key, required this.complaints});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 250,
      child: PieChart(
        PieChartData(
          sections: complaints.map((c) {
            return PieChartSectionData(
              color: _getColor(complaints.indexOf(c)),
              value: c.percentage,
              title: '${c.percentage.toStringAsFixed(1)}%',
              titleStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
              radius: 80,
            );
          }).toList(),
          sectionsSpace: 2,
          centerSpaceRadius: 40,
        ),
      ),
    );
  }

  Color _getColor(int index) {
    final colors = [
      Colors.blue.shade400,
      Colors.cyan.shade400,
      Colors.teal.shade400,
      Colors.green.shade400,
      Colors.orange.shade400,
    ];
    return colors[index % colors.length];
  }
}

class ComplaintLegend extends StatelessWidget {
  final List<ComplaintType> complaints;

  const ComplaintLegend({super.key, required this.complaints});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: complaints.asMap().entries.map((entry) {
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            children: [
              Container(
                width: 16,
                height: 16,
                decoration: BoxDecoration(
                  color: _getColor(entry.key),
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  entry.value.name,
                  style: const TextStyle(fontSize: 14),
                ),
              ),
              Text(
                '${entry.value.count}条',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey.shade400,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Color _getColor(int index) {
    final colors = [
      Colors.blue.shade400,
      Colors.cyan.shade400,
      Colors.teal.shade400,
      Colors.green.shade400,
      Colors.orange.shade400,
    ];
    return colors[index % colors.length];
  }
}