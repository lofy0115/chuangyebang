import "package:flutter/material.dart";
import "../models/business_canvas.dart";
import "../widgets/canvas_cell.dart";

class LeanCanvasScreen extends StatelessWidget {
  final BusinessCanvas canvas;
  const LeanCanvasScreen({super.key, required this.canvas});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("🎯 精益画布"),
        backgroundColor: const Color(0xFF1a1a3e),
        actions: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF00d4ff), Color(0xFF00ff88)]),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Text("${canvas.score}%", style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Container(
        color: const Color(0xFF0f0f23),
        padding: const EdgeInsets.all(12),
        child: GridView.count(
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            CanvasCell(title: "问题 Problem", items: canvas.problem.map((p) => "${p.title} (${p.percentage}%)").toList(), color: const Color(0xFF00d4ff)),
            CanvasCell(title: "解决方案", items: canvas.solution.map((s) => s.title).toList(), color: const Color(0xFF00d4ff)),
            CanvasCell(title: "独特价值主张", items: [canvas.uniqueValueProp], color: const Color(0xFF00ff88)),
            CanvasCell(title: "门槛优势", items: canvas.unfairAdvantage, color: const Color(0xFF00ff88)),
            CanvasCell(title: "关键指标", items: canvas.keyMetrics, color: const Color(0xFF888888)),
            CanvasCell(title: "渠道", items: canvas.channels, color: const Color(0xFF888888)),
            CanvasCell(title: "成本结构", items: [canvas.costStructure], color: const Color(0xFFff6b6b)),
            CanvasCell(title: "收入来源", items: canvas.revenueStreams, color: const Color(0xFF00ff88)),
          ],
        ),
      ),
    );
  }
}