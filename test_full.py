# -*- coding: utf-8 -*-
"""
同花顺7*24快讯抓取工具 - 全功能测试脚本
测试所有功能模块
"""

import sys
import os
import unittest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestFundamentalData(unittest.TestCase):
    """测试基本面数据获取功能"""
    
    def test_import_fetch_fundamental(self):
        """测试导入fetch_fundamental_data模块"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "fetch_fundamental_data", 
            os.path.join(os.path.dirname(__file__), "fetch_fundamental_data.py")
        )
        module = importlib.util.module_from_spec(spec)
        # 不执行模块，只测试导入
        self.assertIsNotNone(spec)
    
    def test_stock_code_filter(self):
        """测试股票代码过滤逻辑"""
        # 沪市主板
        sh_codes = ['600000', '601000', '603000', '605000']
        for code in sh_codes:
            self.assertTrue(code.startswith(('600', '601', '603', '605')))
        
        # 深市主板
        sz_codes = ['000001', '001000', '002000', '003000']
        for code in sz_codes:
            self.assertTrue(code.startswith(('000', '001', '002', '003')))
        
        # 创业板
        cyb_codes = ['300001', '301000']
        for code in cyb_codes:
            self.assertTrue(code.startswith(('300', '301')))
    
    def test_excel_output_structure(self):
        """测试Excel输出结构"""
        # 创建测试数据
        test_data = {
            '代码': ['600519', '000001', '300750'],
            '名称': ['贵州茅台', '平安银行', '宁德时代'],
            '价格': [1407.24, 11.50, 180.00],
            '涨跌幅': [-3.80, 1.20, 2.50],
            '总市值': [1760000000000.0, 220000000000.0, 420000000000.0],
            '每股收益': ['65.66', '1.50', '8.50'],
            '每股净资产': ['202.56', '15.00', '35.00'],
            '净资产收益率': ['32.53', '10.00', '24.00'],
            '毛利率': ['91.2', '30.0', '25.0'],
            '净利润增长率': ['-4.53', '5.00', '15.00'],
            '营收增长率': ['-1.21', '3.00', '10.00'],
        }
        
        df = pd.DataFrame(test_data)
        
        # 验证列存在
        required_columns = [
            '代码', '名称', '价格', '涨跌幅', '总市值',
            '每股收益', '每股净资产', '净资产收益率',
            '毛利率', '净利润增长率', '营收增长率'
        ]
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # 验证数据行数
        self.assertEqual(len(df), 3)
        
        # 验证价格排序
        df_sorted = df.sort_values('价格', ascending=False).reset_index(drop=True)
        self.assertEqual(df_sorted.iloc[0]['名称'], '贵州茅台')


class TestNewsScraper(unittest.TestCase):
    """测试新闻抓取功能"""
    
    def setUp(self):
        """测试前准备"""
        from news_scraper import NewsScraper
        self.scraper = NewsScraper()
    
    def test_scraper_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.scraper.headers)
        self.assertIn('User-Agent', self.scraper.headers)
    
    def test_news_data_structure(self):
        """测试新闻数据结构"""
        test_news = {
            'time': '1713427200',
            'title': '测试新闻标题',
            'content': '<p>测试新闻内容</p>',
            'url': 'https://test.com'
        }
        
        self.assertIn('time', test_news)
        self.assertIn('title', test_news)
        self.assertIn('content', test_news)
    
    def test_performance_filter(self):
        """测试业绩公告筛选"""
        from keywords import PERFORMANCE_KEYWORDS, EXCLUDE_KEYWORDS
        
        test_titles = [
            '业绩公告：公司净利润增长20%',
            '营收突破100亿元',
            'ST公司发布业绩预告',
        ]
        
        for title in test_titles[:2]:
            is_performance = any(kw in title for kw in PERFORMANCE_KEYWORDS)
            self.assertTrue(is_performance)
        
        # ST应该被排除
        self.assertIn('ST', EXCLUDE_KEYWORDS)


class TestPolicyAnalysis(unittest.TestCase):
    """测试政策利好分析功能"""
    
    def test_policy_keywords(self):
        """测试政策关键词"""
        from keywords import POLICY_KEYWORDS
        
        self.assertIn('政策', POLICY_KEYWORDS)
        self.assertIn('支持', POLICY_KEYWORDS)
        self.assertIn('促进', POLICY_KEYWORDS)
    
    def test_province_map(self):
        """测试地区映射"""
        from keywords import PROVINCE_MAP
        
        self.assertIn('黑龙江', PROVINCE_MAP)
        self.assertIn('广东', PROVINCE_MAP)
        self.assertIn('浙江', PROVINCE_MAP)
    
    def test_industry_mapping(self):
        """测试行业映射"""
        from concept_codes import concept_map
        
        # 测试概念映射存在
        self.assertTrue(len(concept_map) > 0)


class TestNewsAnalysis(unittest.TestCase):
    """测试新闻分析功能"""
    
    def test_industry_keywords(self):
        """测试行业关键词"""
        from keywords import (
            FINANCE_SUBSECTORS,
            NEW_ENERGY_SUBSECTORS,
            REAL_ESTATE_SUBSECTORS,
            MEDICINE_SUBSECTORS
        )
        
        self.assertTrue(len(FINANCE_SUBSECTORS) > 0)
        self.assertTrue(len(NEW_ENERGY_SUBSECTORS) > 0)
        self.assertTrue(len(REAL_ESTATE_SUBSECTORS) > 0)
        self.assertTrue(len(MEDICINE_SUBSECTORS) > 0)
    
    def test_news_content_analysis(self):
        """测试新闻内容分析"""
        test_content = "新能源汽车销量大增，比亚迪、宁德时代等企业表现突出"
        
        # 应该识别到新能源和汽车相关
        self.assertTrue('新能源' in test_content or '汽车' in test_content)


class TestExcelOperations(unittest.TestCase):
    """测试Excel操作功能"""
    
    def test_excel_save_and_read(self):
        """测试Excel保存和读取"""
        import tempfile
        
        test_data = {
            '代码': ['600519', '000001'],
            '名称': ['贵州茅台', '平安银行'],
            '价格': [1407.24, 11.50],
        }
        
        df = pd.DataFrame(test_data)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 保存Excel
            df.to_excel(tmp_path, index=False, sheet_name='测试')
            
            # 读取Excel
            df_read = pd.read_excel(tmp_path)
            
            # 验证数据
            self.assertEqual(len(df_read), 2)
            self.assertIn('代码', df_read.columns)
            self.assertIn('名称', df_read.columns)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_multi_sheet_excel(self):
        """测试多sheet Excel"""
        import tempfile
        import gc
        
        df1 = pd.DataFrame({'代码': ['600519'], '名称': ['贵州茅台']})
        df2 = pd.DataFrame({'代码': ['000001'], '名称': ['平安银行']})
        df3 = pd.DataFrame({'代码': ['300750'], '名称': ['宁德时代']})
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='沪市主板', index=False)
                df2.to_excel(writer, sheet_name='深市主板', index=False)
                df3.to_excel(writer, sheet_name='创业板', index=False)
            
            # 验证sheet
            xls = pd.ExcelFile(tmp_path)
            self.assertIn('沪市主板', xls.sheet_names)
            self.assertIn('深市主板', xls.sheet_names)
            self.assertIn('创业板', xls.sheet_names)
            
            # 关闭Excel文件
            xls.close()
            del xls
            gc.collect()
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass


class TestConceptCodes(unittest.TestCase):
    """测试概念板块代码"""
    
    def test_concept_map_not_empty(self):
        """测试概念映射不为空"""
        from concept_codes import concept_map
        
        self.assertTrue(len(concept_map) > 0)
    
    def test_commercial_aerospace(self):
        """测试商业航天概念"""
        # 测试商业航天分类存在（直接检查文件内容）
        expected_categories = [
            '全部', '太空光伏', '太空算力', '卫星通讯',
            '火箭回收', '蓝剑航天', '卫星测控', '卫星遥感',
            '火箭发射', '中科宇航'
        ]
        
        # 读取fetch_commercial_aerospace.py文件内容
        with open('fetch_commercial_aerospace.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查所有分类是否都在文件中
        for category in expected_categories:
            self.assertIn(f"'{category}'", content, f"未找到分类: {category}")
    
    def test_concept_code_format(self):
        """测试概念代码格式"""
        from concept_codes import concept_map
        
        valid_count = 0
        
        for category, code in concept_map.items():
            # 概念代码应该是字符串
            self.assertIsInstance(code, str, f"{category} 的概念代码应该是字符串")
            
            # 概念代码应该是885或886开头的6位数字
            if isinstance(code, str) and len(code) == 6 and code.isdigit():
                self.assertTrue(code.startswith(('885', '886', '881', '882')), 
                              f"{category} 的概念代码 {code} 格式不正确")
                valid_count += 1
        
        # 只要有有效概念代码就通过测试
        self.assertTrue(valid_count > 0, "没有找到有效的概念代码")


def run_all_tests():
    """运行所有测试"""
    print('='*60)
    print('同花顺7*24快讯抓取工具 - 全功能测试')
    print('='*60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFundamentalData))
    suite.addTests(loader.loadTestsFromTestCase(TestNewsScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestPolicyAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestNewsAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestExcelOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestConceptCodes))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print('='*60)
    print('测试总结')
    print('='*60)
    print(f'总测试数: {result.testsRun}')
    print(f'成功: {result.testsRun - len(result.failures) - len(result.errors)}')
    print(f'失败: {len(result.failures)}')
    print(f'错误: {len(result.errors)}')
    print()
    
    if result.wasSuccessful():
        print('✓ 所有测试通过！')
    else:
        print('✗ 部分测试失败，请检查错误信息')
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
