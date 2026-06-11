import "package:flutter/material.dart";
import "../models/business_canvas.dart";
import "../widgets/canvas_cell.dart";

class BusinessCanvasScreen extends StatelessWidget {
  final BusinessCanvas canvas;
  const BusinessCanvasScreen({super.key, required this.canvas});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("📋 商业模式画布"), backgroundColor: const Color(0xFF1a1a3e)),
      body: Container(
        color: const Color(0xFF0f0f23),
        padding: const EdgeInsets.all(12),
        child: GridView.count(
          crossAxisCount: 3,
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          childAspectRatio: 1.0,
          children: [
            CanvasCell(title: "客户细分", items: canvas.customerSegments, color: const Color(0xFF00d4ff)),
            CanvasCell(title: "价值主张", items: canvas.valuePropositions, color: const Color(0xFF00ff88)),
            CanvasCell(title: "渠道", items: canvas.channels, color: const Color(0xFF00d4ff)),
            CanvasCell(title: "客户关系", items: canvas.customerRelationships, color: const Color(0xFF888888)),
            CanvasCell(title: "收入来源", items: canvas.revenueStreams, color: const Color(0xFF00ff88)),
            CanvasCell(title: "核心资源", items: canvas.keyResources, color: const Color(0xFF888888)),
            CanvasCell(title: "关键活动", items: canvas.keyActivities, color: const Color(0xFF888888)),
            CanvasCell(title: "合作伙伴", items: canvas.keyPartners, color: const Color(0xFF888888)),
            CanvasCell(title: "成本结构", items: [canvas.costStructure], color: const Color(0xFFff6b6b)),
          ],
        ),
      ),
    );
  }
}