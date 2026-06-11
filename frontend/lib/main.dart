import "package:flutter/material.dart";
import "screens/home_screen.dart";
import "theme/app_theme.dart";

void main() {
  runApp(const ChuangYeBangApp());
}

class ChuangYeBangApp extends StatelessWidget {
  const ChuangYeBangApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "创业帮",
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeScreen(),
    );
  }
}