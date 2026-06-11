import 'package:flutter/material.dart';

class SearchBox extends StatefulWidget {
  final Function(String) onSearch;
  final String? initialValue;

  const SearchBox({
    super.key,
    required this.onSearch,
    this.initialValue,
  });

  @override
  State<SearchBox> createState() => _SearchBoxState();
}

class _SearchBoxState extends State<SearchBox> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF2D2D2D),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const SizedBox(width: 16),
          const Icon(Icons.search, color: Colors.grey),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: const InputDecoration(
                hintText: '输入消费者抱怨关键词...',
                hintStyle: TextStyle(color: Colors.grey),
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(vertical: 16),
              ),
              style: const TextStyle(fontSize: 16),
              onSubmitted: (value) {
                if (value.isNotEmpty) {
                  widget.onSearch(value);
                }
              },
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send, color: Colors.blue),
            onPressed: () {
              if (_controller.text.isNotEmpty) {
                widget.onSearch(_controller.text);
              }
            },
          ),
        ],
      ),
    );
  }
}