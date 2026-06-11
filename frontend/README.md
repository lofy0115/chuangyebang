# 创业帮 Flutter App

从消费者抱怨到商业模式的创新分析工具。

## 功能特性

- 消费者抱怨分析
- 精益画布生成
- 商业模式画布生成
- 数据源覆盖展示

## 运行方式

```bash
cd frontend
flutter pub get
flutter run
```

## 项目结构

```
lib/
├── main.dart          # 主入口
├── config/            # 配置
├── models/            # 数据模型
├── screens/           # 页面
├── services/          # API服务
├── theme/             # 主题
└── widgets/           # 组件
```

## API配置

默认后端地址: http://localhost:8000

可在 lib/config/api_config.dart 中修改。