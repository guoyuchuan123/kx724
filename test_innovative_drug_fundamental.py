# -*- coding: utf-8 -*-
"""
测试创新药和基本面数据功能
"""

import sys
import os
import unittest
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestInnovativeDrug(unittest.TestCase):
    """测试创新药概念板块"""
    
    def test_file_exists(self):
        """测试文件存在"""
        self.assertTrue(os.path.exists('fetch_innovative_drug.py'))
    
    def test_stock_list_defined(self):
        """测试股票列表已定义"""
        with open('fetch_innovative_drug.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('innovative_drug_names', content)
        self.assertIn('恒瑞医药', content)
        self.assertIn('药明康德', content)
    
    def test_api_url_defined(self):
        """测试API URL已定义"""
        with open('fetch_innovative_drug.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('10jqka.com.cn', content)
        self.assertIn('multi_last_snapshot', content)
    
    def test_data_fields_defined(self):
        """测试数据字段已定义"""
        with open('fetch_innovative_drug.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('data_fields', content)
    
    def test_excel_output_structure(self):
        """测试Excel输出结构（验证代码逻辑）"""
        with open('fetch_innovative_drug.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证Excel输出逻辑
        self.assertIn('ExcelWriter', content)
        self.assertIn('创新药', content)
        self.assertIn('to_excel', content)
        self.assertIn('news_data', content)


class TestFundamentalData(unittest.TestCase):
    """测试基本面数据功能"""
    
    def test_file_exists(self):
        """测试文件存在"""
        self.assertTrue(os.path.exists('fetch_fundamental_data.py'))
    
    def test_imports_defined(self):
        """测试导入模块已定义"""
        with open('fetch_fundamental_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('akshare', content)
        self.assertIn('ThreadPoolExecutor', content)
    
    def test_api_urls_defined(self):
        """测试API URL已定义"""
        with open('fetch_fundamental_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('finance.sina.com.cn', content)
        self.assertIn('qt.gtimg.cn', content)
    
    def test_market_segments_defined(self):
        """测试市场分段已定义"""
        with open('fetch_fundamental_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('沪市主板', content)
        self.assertIn('深市主板', content)
        self.assertIn('创业板', content)
    
    def test_financial_fields_defined(self):
        """测试财务字段已定义"""
        with open('fetch_fundamental_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        financial_fields = [
            '每股收益', '每股净资产', '净资产收益率',
            '毛利率', '净利润增长率', '营收增长率'
        ]
        for field in financial_fields:
            self.assertIn(field, content, f"未找到财务字段: {field}")
    
    def test_excel_output_structure(self):
        """测试Excel输出结构（验证代码逻辑）"""
        with open('fetch_fundamental_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证Excel输出逻辑
        self.assertIn('ExcelWriter', content)
        self.assertIn('沪市主板', content)
        self.assertIn('深市主板', content)
        self.assertIn('创业板', content)
        self.assertIn('to_excel', content)


def run_all_tests():
    """运行所有测试"""
    print('='*60)
    print('功能测试')
    print('测试: 创新药、基本面数据')
    print('='*60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestInnovativeDrug))
    suite.addTests(loader.loadTestsFromTestCase(TestFundamentalData))
    
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
