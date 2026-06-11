import '../models/analysis_result.dart';
import '../models/complaint_type.dart';
import '../models/customer_segment.dart';
import '../models/business_canvas.dart';
import '../models/lean_canvas.dart';

class MockDataService {
  static AnalysisResult getMockAnalysis(String query) {
    return AnalysisResult(
      id: 'mock_${DateTime.now().millisecondsSinceEpoch}',
      searchQuery: query,
      timestamp: DateTime.now(),
      complaintTypes: [
        ComplaintType(
          id: '1',
          name: '配送速度慢',
          description: '消费者抱怨配送时间过长',
          count: 1250,
          percentage: 35.0,
          relatedProducts: ['生鲜', '外卖', '电商'],
          suggestions: ['建立前置仓', '优化物流路线', '提升配送效率'],
        ),
        ComplaintType(
          id: '2',
          name: '质量不达标',
          description: '产品质量与描述不符',
          count: 890,
          percentage: 25.0,
          relatedProducts: ['电商', '美妆', '食品'],
          suggestions: ['严格品控', '如实描述', '退换货保障'],
        ),
        ComplaintType(
          id: '3',
          name: '价格虚高',
          description: '价格比竞争对手高',
          count: 720,
          percentage: 20.0,
          relatedProducts: ['电商', '旅游', '教育'],
          suggestions: ['成本优化', '批量采购', '差异化定价'],
        ),
        ComplaintType(
          id: '4',
          name: '服务态度差',
          description: '客服响应慢且态度不佳',
          count: 450,
          percentage: 13.0,
          relatedProducts: ['电商', '金融', '教育'],
          suggestions: ['培训客服', '智能客服', '优化流程'],
        ),
        ComplaintType(
          id: '5',
          name: '售后困难',
          description: '退换货流程复杂',
          count: 270,
          percentage: 7.0,
          relatedProducts: ['电商', '家电', '家具'],
          suggestions: ['简化流程', '上门取件', '快速退款'],
        ),
      ],
      customerSegments: [
        CustomerSegment(
          id: '1',
          name: '年轻上班族',
          description: '25-35岁,工作繁忙,注重效率',
          size: 25000000,
          spending: 5000,
          painPoints: ['时间宝贵', '选择困难', '品质担忧'],
          needs: ['快速配送', '品质保障', '便捷服务'],
          behaviorPattern: '高频低价,复购率高',
        ),
        CustomerSegment(
          id: '2',
          name: '家庭主妇',
          description: '30-45岁,负责家庭采购,注重性价比',
          size: 18000000,
          spending: 8000,
          painPoints: ['价格敏感', '品质不确定', '选择太多'],
          needs: ['优惠活动', '正品保障', '丰富选择'],
          behaviorPattern: '周期性采购,注重评价',
        ),
        CustomerSegment(
          id: '3',
          name: '学生群体',
          description: '18-25岁,预算有限,追求新鲜',
          size: 30000000,
          spending: 2000,
          painPoints: ['预算有限', '正品担忧'],
          needs: ['学生优惠', '正品保证', '潮流新品'],
          behaviorPattern: '受社交影响大,价格敏感',
        ),
      ],
      dataSourceCoverage: {
        '电商平台': 85,
        '社交媒体': 72,
        '客服记录': 65,
        '评价系统': 90,
        '论坛社区': 55,
      },
      summary: '通过对消费者抱怨数据的分析,我们发现了配送、质量、价格等服务方面的核心痛点。建议针对年轻上班族和家庭主妇两大核心群体,优化配送效率和产品品质,同时通过差异化定价策略提升竞争力。',
    );
  }

  static AnalysisResult getMockLeanCanvas(String query) {
    final baseAnalysis = getMockAnalysis(query);
    return AnalysisResult(
      id: baseAnalysis.id,
      searchQuery: query,
      timestamp: DateTime.now(),
      complaintTypes: baseAnalysis.complaintTypes,
      customerSegments: baseAnalysis.customerSegments,
      dataSourceCoverage: baseAnalysis.dataSourceCoverage,
      summary: baseAnalysis.summary,
      leanCanvas: LeanCanvas(
        problem: '消费者抱怨配送慢、质量差、价格高',
        solution: '建立快速配送网络+严格品控+动态定价',
        keyMetrics: '配送时效,用户满意度,复购率',
        uniqueValue: '30分钟送达,品质保障,价格最优',
        unfairAdvantage: '自建物流体系,供应链整合',
        channels: 'APP,微信小程序,线下门店',
        costStructure: '物流成本,人力成本,营销成本',
        revenueStreams: '商品销售,会员费,广告收入',
      ),
    );
  }

  static AnalysisResult getMockBusinessCanvas(String query) {
    final baseAnalysis = getMockAnalysis(query);
    return AnalysisResult(
      id: baseAnalysis.id,
      searchQuery: query,
      timestamp: DateTime.now(),
      complaintTypes: baseAnalysis.complaintTypes,
      customerSegments: baseAnalysis.customerSegments,
      dataSourceCoverage: baseAnalysis.dataSourceCoverage,
      summary: baseAnalysis.summary,
      businessCanvas: BusinessCanvas(
        keyPartners: '供应商,物流公司,仓储服务商',
        keyActivities: '商品采购,仓储管理,配送服务,用户运营',
        keyResources: '物流网络,技术平台,用户数据,品牌',
        valuePropositions: '快速配送,正品保障,价格优惠,优质服务',
        customerRelationships: '在线客服,会员体系,社区运营',
        channels: '移动APP,微信小程序,线下门店,社交媒体',
        customerSegments: '年轻上班族(25-35岁),家庭主妇(30-45岁),学生群体(18-25岁)',
        costStructure: '物流成本40%,人力成本25%,营销成本15%,技术成本10%,其他10%',
        revenueStreams: '商品销售80%,会员收入12%,广告收入8%',
      ),
    );
  }
}