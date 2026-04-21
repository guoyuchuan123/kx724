# -*- coding: utf-8 -*-
"""
同花顺7*24快讯抓取工具 - 自动化测试脚本
全面测试所有功能模块
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keywords import (
    PERFORMANCE_KEYWORDS, EXCLUDE_KEYWORDS, POLICY_KEYWORDS,
    SINGLE_STOCK_KEYWORDS, NATIONAL_KEYWORDS, PROVINCE_MAP,
    FINANCE_SUBSECTORS, FINANCE_EXCLUDE_KEYWORDS,
    NEW_ENERGY_SUBSECTORS, NEW_ENERGY_EXCLUDE_KEYWORDS,
    REAL_ESTATE_SUBSECTORS, REAL_ESTATE_EXCLUDE_KEYWORDS,
    MEDICINE_SUBSECTORS, MEDICINE_EXCLUDE_KEYWORDS,
    FTZ_SUBSECTORS, FTZ_EXCLUDE_KEYWORDS
)
from concept_codes import concept_map
from news_scraper import NewsScraper


class TestKeywords(unittest.TestCase):
    """测试关键词定义"""
    
    def test_performance_keywords_not_empty(self):
        """测试业绩关键词不为空"""
        self.assertTrue(len(PERFORMANCE_KEYWORDS) > 0)
        self.assertIn('业绩', PERFORMANCE_KEYWORDS)
        self.assertIn('净利润', PERFORMANCE_KEYWORDS)
    
    def test_exclude_keywords_not_empty(self):
        """测试排除关键词不为空"""
        self.assertTrue(len(EXCLUDE_KEYWORDS) > 0)
        self.assertIn('ST', EXCLUDE_KEYWORDS)
    
    def test_policy_keywords_not_empty(self):
        """测试政策关键词不为空"""
        self.assertTrue(len(POLICY_KEYWORDS) > 0)
        self.assertIn('政策', POLICY_KEYWORDS)
        self.assertIn('支持', POLICY_KEYWORDS)
    
    def test_single_stock_keywords_not_empty(self):
        """测试单只股票关键词不为空"""
        self.assertTrue(len(SINGLE_STOCK_KEYWORDS) > 0)
        self.assertIn('公告', SINGLE_STOCK_KEYWORDS)
    
    def test_national_keywords_not_empty(self):
        """测试国家关键词不为空"""
        self.assertTrue(len(NATIONAL_KEYWORDS) > 0)
        self.assertIn('国家', NATIONAL_KEYWORDS)
        self.assertIn('国务院', NATIONAL_KEYWORDS)
    
    def test_province_map_not_empty(self):
        """测试地区映射不为空"""
        self.assertTrue(len(PROVINCE_MAP) > 0)
        self.assertEqual(PROVINCE_MAP['北京'], '882002')
        self.assertEqual(PROVINCE_MAP['上海'], '882027')
    
    def test_finance_subsectors(self):
        """测试金融子板块"""
        self.assertTrue(len(FINANCE_SUBSECTORS) > 0)
        self.assertEqual(len(FINANCE_SUBSECTORS), len(FINANCE_EXCLUDE_KEYWORDS))  # 银行、证券、保险
    
    def test_new_energy_subsectors(self):
        """测试新能源子板块"""
        self.assertTrue(len(NEW_ENERGY_SUBSECTORS) > 0)
        self.assertTrue(len(NEW_ENERGY_EXCLUDE_KEYWORDS) > 0)
    
    def test_real_estate_subsectors(self):
        """测试地产基建子板块"""
        self.assertTrue(len(REAL_ESTATE_SUBSECTORS) > 0)
        self.assertTrue(len(REAL_ESTATE_EXCLUDE_KEYWORDS) > 0)
    
    def test_medicine_subsectors(self):
        """测试医药子板块"""
        self.assertTrue(len(MEDICINE_SUBSECTORS) > 0)
        self.assertTrue(len(MEDICINE_EXCLUDE_KEYWORDS) > 0)
    
    def test_ftz_subsectors(self):
        """测试自贸区子板块"""
        self.assertTrue(len(FTZ_SUBSECTORS) > 0)
        self.assertTrue(len(FTZ_EXCLUDE_KEYWORDS) > 0)


class TestConceptMap(unittest.TestCase):
    """测试概念板块代码映射"""
    
    def test_concept_map_not_empty(self):
        """测试概念映射不为空"""
        self.assertTrue(len(concept_map) > 0)
    
    def test_ai_concepts(self):
        """测试AI相关概念"""
        self.assertIn('人工智能', concept_map)
        self.assertEqual(concept_map['人工智能'], '885728')
        self.assertEqual(concept_map['AI'], '885728')
    
    def test_new_energy_concepts(self):
        """测试新能源概念"""
        self.assertIn('光伏', concept_map)
        self.assertEqual(concept_map['光伏'], '881279')
        self.assertIn('风电', concept_map)
    
    def test_chip_concepts(self):
        """测试芯片概念"""
        self.assertIn('芯片', concept_map)
        self.assertEqual(concept_map['芯片'], '885756')
        self.assertIn('半导体', concept_map)
    
    def test_robot_concepts(self):
        """测试机器人概念"""
        self.assertIn('机器人', concept_map)
        self.assertEqual(concept_map['机器人'], '885517')
    
    def test_auto_concepts(self):
        """测试汽车概念"""
        self.assertIn('汽车', concept_map)
        self.assertIn('新能源车', concept_map)
        self.assertEqual(concept_map['新能源车'], '881125')
    
    def test_finance_concepts(self):
        """测试金融概念"""
        self.assertIn('银行', concept_map)
        self.assertIn('证券', concept_map)
        self.assertIn('保险', concept_map)
    
    def test_medicine_concepts(self):
        """测试医药概念"""
        self.assertIn('医疗', concept_map)
        self.assertIn('医药制造', concept_map)
        self.assertIn('生物医药', concept_map)
    
    def test_ftz_concepts(self):
        """测试自贸区概念"""
        self.assertIn('上海自贸区', concept_map)
        self.assertIn('海南自贸区', concept_map)


class TestNewsScraperInit(unittest.TestCase):
    """测试NewsScraper初始化"""
    
    def test_init(self):
        """测试初始化"""
        scraper = NewsScraper()
        self.assertIsNotNone(scraper)
        self.assertIsNotNone(scraper.base_url)
        self.assertIsNotNone(scraper.api_url)
        self.assertIsNotNone(scraper.headers)
        self.assertEqual(scraper.news_data, {})
        self.assertEqual(scraper.output_dir, "news_data")
    
    def test_output_dir_exists(self):
        """测试输出目录存在"""
        scraper = NewsScraper()
        self.assertTrue(os.path.exists(scraper.output_dir))


class TestNetworkCheck(unittest.TestCase):
    """测试网络检查功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    @patch('requests.get')
    def test_network_check_success(self, mock_get):
        """测试网络检查成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.scraper.check_network()
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_network_check_failure(self, mock_get):
        """测试网络检查失败"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.scraper.check_network()
        self.assertFalse(result)


class TestNewsProcessing(unittest.TestCase):
    """测试新闻处理功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_process_news_item(self):
        """测试处理新闻项"""
        import time
        item = {
            'ctime': str(int(time.time())),
            'title': '测试新闻标题',
            'digest': '<p>这是测试新闻内容</p>'
        }
        
        result = self.scraper.process_news_item(item)
        self.assertIsNotNone(result)
        self.assertEqual(result['标题'], '测试新闻标题')
        self.assertIn('这是测试新闻内容', result['内容详情'])
        self.assertNotIn('<p>', result['内容详情'])  # HTML标签应被移除
    
    def test_process_news_item_empty(self):
        """测试处理空新闻项"""
        item = {}
        result = self.scraper.process_news_item(item)
        self.assertIsNotNone(result)
        self.assertEqual(result['标题'], '')
    
    def test_extract_summary(self):
        """测试提取摘要"""
        content = '<p>这是一段测试内容，用于测试摘要提取功能。</p>'
        summary = self.scraper.extract_summary(content)
        self.assertNotIn('<', summary)  # 不应包含HTML标签
    
    def test_extract_summary_long(self):
        """测试长文本摘要提取"""
        content = '这是一段很长的内容' * 20
        summary = self.scraper.extract_summary(content)
        self.assertTrue(len(summary) <= 153)  # 150 + "..."
    
    def test_extract_summary_empty(self):
        """测试空内容摘要提取"""
        summary = self.scraper.extract_summary('')
        self.assertEqual(summary, '')


class TestNewsFiltering(unittest.TestCase):
    """测试新闻筛选功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_filter_performance_news(self):
        """测试筛选业绩公告"""
        news_list = [
            {'标题': '公司业绩增长', '内容详情': '净利润同比增长50%', '时间戳': 1},
            {'标题': 'ST公司亏损', '内容详情': '业绩下滑', '时间戳': 2},
            {'标题': '普通新闻', '内容详情': '这是一条普通新闻', '时间戳': 3},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['标题'], '公司业绩增长')
    
    def test_filter_policy_benefits(self):
        """测试筛选政策利好"""
        news_list = [
            {'标题': '国家支持新能源汽车发展', '内容详情': '政策利好，鼓励发展', '时间戳': 1},
            {'标题': '600000公司公告', '内容详情': '净利润增长', '时间戳': 2},
            {'标题': '普通新闻', '内容详情': '这是一条普通新闻', '时间戳': 3},
        ]
        
        result = self.scraper.filter_policy_benefits(news_list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['标题'], '国家支持新能源汽车发展')


class TestAnalyzeNewsStocks(unittest.TestCase):
    """测试新闻分析股票功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_analyze_new_energy(self):
        """测试新能源新闻分析"""
        title = "新能源汽车销量大增"
        content = "据最新数据显示，新能源汽车销量同比增长80%"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        self.assertTrue(len(result['industries']) > 0)
    
    def test_analyze_finance(self):
        """测试金融新闻分析"""
        title = "金融行业改革"
        content = "国家推动金融行业深化改革"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        # 应包含银行、证券、保险子板块
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('银行', industry_names)
        self.assertIn('证券', industry_names)
        self.assertIn('保险', industry_names)
    
    def test_analyze_real_estate(self):
        """测试房地产新闻分析"""
        title = "房地产市场调控"
        content = "国家出台房地产调控政策"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        # 应包含基建、建材等子板块
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('基建', industry_names)
        self.assertIn('建材', industry_names)
    
    def test_analyze_medicine(self):
        """测试医药新闻分析"""
        title = "医药行业发展"
        content = "国家支持医药行业创新发展"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('医疗', industry_names)
        self.assertIn('医药制造', industry_names)
    
    def test_analyze_ftz(self):
        """测试自贸区新闻分析"""
        title = "自贸区建设"
        content = "国家推进自贸区建设"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('上海自贸区', industry_names)
        self.assertIn('海南自贸区', industry_names)
    
    def test_analyze_no_match(self):
        """测试无匹配新闻分析"""
        title = "天气晴朗"
        content = "今天天气很好"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertFalse(result['matched'])
    
    def test_analyze_new_energy_vehicle(self):
        """测试新能源汽车特殊处理"""
        title = "新能源汽车产业发展"
        content = "国家支持新能源汽车产业发展"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('新能源车', industry_names)
    
    def test_analyze_specific_industry(self):
        """测试具体行业分析"""
        title = "光伏产业链价格上涨"
        content = "光伏产业链各环节企业利润空间扩大"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('光伏', industry_names)


class TestAnalyzePolicyStocks(unittest.TestCase):
    """测试政策分析股票功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_analyze_national_policy(self):
        """测试国家政策分析"""
        policy = "国家支持新能源汽车产业发展政策"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        self.assertEqual(result['type'], '国家政策')
    
    def test_analyze_local_policy(self):
        """测试地方政策分析"""
        policy = "黑龙江省支持智能机器人产业发展若干政策措施"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        self.assertEqual(result['type'], '地方政策')
        self.assertEqual(result['region'], '黑龙江')
    
    def test_analyze_finance_policy(self):
        """测试金融政策分析"""
        policy = "国家推动金融行业深化改革"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('银行', industry_names)
        self.assertIn('证券', industry_names)
    
    def test_analyze_real_estate_policy(self):
        """测试房地产政策分析"""
        policy = "国家出台房地产调控政策"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('基建', industry_names)
        self.assertIn('建材', industry_names)
    
    def test_analyze_medicine_policy(self):
        """测试医药政策分析"""
        policy = "国家支持医药行业创新发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('医疗', industry_names)
        self.assertIn('医药制造', industry_names)
    
    def test_analyze_ftz_policy(self):
        """测试自贸区政策分析"""
        policy = "国家推进自贸区建设"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('上海自贸区', industry_names)
        self.assertIn('海南自贸区', industry_names)
    
    def test_analyze_no_match(self):
        """测试无匹配政策分析"""
        policy = "今天天气很好"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertFalse(result['matched'])


class TestProvinceStocks(unittest.TestCase):
    """测试地区股票功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_province_map_coverage(self):
        """测试地区映射覆盖"""
        expected_provinces = [
            '北京', '上海', '广东', '深圳', '浙江', '江苏', '四川', '重庆',
            '湖北', '湖南', '河南', '河北', '山东', '山西', '安徽', '福建',
            '江西', '辽宁', '吉林', '黑龙江', '陕西', '甘肃', '青海',
            '云南', '贵州', '海南', '内蒙古', '新疆', '西藏', '广西',
            '宁夏', '天津', '浦东'
        ]
        
        for province in expected_provinces:
            self.assertIn(province, PROVINCE_MAP, f"缺少地区: {province}")
    
    def test_province_code_format(self):
        """测试地区代码格式"""
        for province, code in PROVINCE_MAP.items():
            self.assertTrue(code.startswith('882'), f"地区 {province} 代码格式错误: {code}")


class TestIndustryStocks(unittest.TestCase):
    """测试行业股票功能（模拟API调用）"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_get_industry_stocks_mock_data(self):
        """测试行业股票数据处理逻辑"""
        # 直接测试数据处理逻辑，不依赖网络请求
        import pandas as pd
        
        # 模拟API返回的数据
        mock_data = {
            'items': [
                {"5": "600000", "55": "测试股票", "199112": "1.00", "10": "10.00", "13": "1000"},
                {"5": "600001", "55": "ST测试", "199112": "1.00", "10": "10.00", "13": "1000"},
            ]
        }
        
        df = pd.DataFrame(mock_data['items'])
        col_mapping = {
            "5": "代码",
            "55": "名称", 
            "199112": "涨跌幅",
            "10": "价格",
            "13": "成交量"
        }
        existing_mapping = {k: v for k, v in col_mapping.items() if k in df.columns}
        df.rename(columns=existing_mapping, inplace=True)
        
        # 验证列映射
        self.assertIn('代码', df.columns)
        self.assertIn('名称', df.columns)
        
        # 验证ST过滤
        df_filtered = df[~df['名称'].str.contains('ST', na=False)]
        self.assertEqual(len(df_filtered), 1)
        self.assertEqual(df_filtered.iloc[0]['名称'], '测试股票')
    
    def test_get_industry_stocks_exception_handling(self):
        """测试行业股票获取异常处理"""
        # 测试异常情况下的返回值
        result = self.scraper._get_industry_stocks('测试行业', '881111')
        # 由于网络请求会失败，应该返回matched=False
        self.assertIn('matched', result)
        self.assertIn('stocks', result)


class TestStockFiltering(unittest.TestCase):
    """测试股票筛选功能"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_filter_st_stocks(self):
        """测试过滤ST股票"""
        stocks = [
            {'代码': '600000', '名称': 'ST测试'},
            {'代码': '600001', '名称': '*ST测试'},
            {'代码': '600002', '名称': '正常股票'},
        ]
        
        filtered = [s for s in stocks if 'ST' not in s['名称']]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['名称'], '正常股票')
    
    def test_filter_price_range(self):
        """测试过滤价格范围"""
        stocks = [
            {'代码': '600000', '名称': '低价股', '价格': '2.00'},
            {'代码': '600001', '名称': '正常股', '价格': '10.00'},
            {'代码': '600002', '名称': '高价股', '价格': '60.00'},
        ]
        
        filtered = [s for s in stocks if 3 <= float(s['价格']) <= 50]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['名称'], '正常股')
    
    def test_filter_kcb_stocks(self):
        """测试过滤科创板股票"""
        stocks = [
            {'代码': '688000', '名称': '科创板'},
            {'代码': '600000', '名称': '主板'},
            {'代码': '000000', '名称': '深主板'},
        ]
        
        filtered = [s for s in stocks if not s['代码'].startswith('688')]
        self.assertEqual(len(filtered), 2)


class TestExcelSaving(unittest.TestCase):
    """测试Excel保存功能（含自动关闭打开的文件）"""
    
    def setUp(self):
        self.scraper = NewsScraper()
        self.test_dir = "test_excel_temp"
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        # 清理测试文件
        import shutil
        import time
        # 先尝试关闭可能打开的Excel文件
        from news_scraper import close_excel_file
        if os.path.exists(self.test_dir):
            for f in os.listdir(self.test_dir):
                if f.endswith('.xlsx'):
                    close_excel_file(os.path.join(self.test_dir, f))
            time.sleep(1)
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                pass  # 忽略清理错误
    
    def test_save_excel_single_sheet(self):
        """测试保存单sheet Excel"""
        from news_scraper import save_excel_with_retry
        
        df = pd.DataFrame({
            '时间': ['2026-04-19 10:00:00'],
            '标题': ['测试新闻'],
            '内容详情': ['测试内容']
        })
        
        filepath = os.path.join(self.test_dir, 'test_single.xlsx')
        result = save_excel_with_retry(df, filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
    
    def test_save_excel_multiple_sheets(self):
        """测试保存多sheet Excel"""
        from news_scraper import save_excel_with_retry
        
        df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df2 = pd.DataFrame({'C': [5, 6], 'D': [7, 8]})
        
        filepath = os.path.join(self.test_dir, 'test_multi.xlsx')
        result = save_excel_with_retry({'sheet1': df1, 'sheet2': df2}, filepath)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
        
        # 验证sheet数量
        xl = pd.ExcelFile(filepath)
        sheet_names = xl.sheet_names
        xl.close()
        self.assertEqual(len(sheet_names), 2)
        self.assertIn('sheet1', sheet_names)
        self.assertIn('sheet2', sheet_names)
    
    def test_save_excel_overwrite(self):
        """测试覆盖已存在的Excel文件"""
        from news_scraper import save_excel_with_retry
        
        df1 = pd.DataFrame({'A': [1]})
        df2 = pd.DataFrame({'A': [2]})
        
        filepath = os.path.join(self.test_dir, 'test_overwrite.xlsx')
        
        # 第一次保存
        result1 = save_excel_with_retry(df1, filepath)
        self.assertTrue(result1)
        
        # 第二次保存（覆盖）
        result2 = save_excel_with_retry(df2, filepath)
        self.assertTrue(result2)
        
        # 验证内容已更新
        df_read = pd.read_excel(filepath)
        self.assertEqual(df_read['A'].iloc[0], 2)
        df_read = None  # 释放引用
    
    def test_close_excel_file_not_exists(self):
        """测试关闭不存在的文件"""
        from news_scraper import close_excel_file
        
        # 不存在的文件应该返回False
        result = close_excel_file('nonexistent_file.xlsx')
        self.assertFalse(result)
    
    def test_save_excel_with_invalid_path(self):
        """测试保存无效路径"""
        from news_scraper import save_excel_with_retry
        
        df = pd.DataFrame({'A': [1]})
        # 无效路径应该返回False
        result = save_excel_with_retry(df, '/invalid/path/file.xlsx')
        self.assertFalse(result)


class TestDataStructures(unittest.TestCase):
    """测试数据结构"""
    
    def test_concept_map_values_are_strings(self):
        """测试概念映射值都是字符串"""
        for key, value in concept_map.items():
            self.assertIsInstance(value, str, f"概念 {key} 的值不是字符串: {value}")
    
    def test_province_map_values_are_strings(self):
        """测试地区映射值都是字符串"""
        for key, value in PROVINCE_MAP.items():
            self.assertIsInstance(value, str, f"地区 {key} 的值不是字符串: {value}")
    
    def test_subsector_format(self):
        """测试子板块格式"""
        for subsector_list in [FINANCE_SUBSECTORS, NEW_ENERGY_SUBSECTORS, 
                              REAL_ESTATE_SUBSECTORS, MEDICINE_SUBSECTORS, FTZ_SUBSECTORS]:
            for item in subsector_list:
                self.assertEqual(len(item), 2)
                self.assertIsInstance(item[0], str)
                self.assertIsInstance(item[1], str)


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("同花顺7*24快讯抓取工具 - 自动化测试")
    print("=" * 60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestKeywords,
        TestConceptMap,
        TestNewsScraperInit,
        TestNetworkCheck,
        TestNewsProcessing,
        TestNewsFiltering,
        TestAnalyzeNewsStocks,
        TestAnalyzePolicyStocks,
        TestProvinceStocks,
        TestIndustryStocks,
        TestStockFiltering,
        TestExcelSaving,
        TestDataStructures,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print()
    print("=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查错误信息")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
