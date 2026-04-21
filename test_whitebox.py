# -*- coding: utf-8 -*-
"""
同花顺7*24快讯抓取工具 - 白盒测试脚本
测试内部逻辑、代码分支、边界条件和异常处理
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
import time

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
from news_scraper import NewsScraper, close_excel_file, save_excel_with_retry


class TestNewsScraperInit(unittest.TestCase):
    """白盒测试：初始化逻辑"""
    
    def test_init_attributes(self):
        """测试初始化属性设置"""
        scraper = NewsScraper()
        
        # 验证所有属性
        self.assertEqual(scraper.base_url, "https://www.10jqka.com.cn/")
        self.assertEqual(scraper.api_url, "https://news.10jqka.com.cn/tapp/news/push/stock/")
        self.assertIsInstance(scraper.headers, dict)
        self.assertIn('User-Agent', scraper.headers)
        self.assertIn('Accept', scraper.headers)
        self.assertEqual(scraper.news_data, {})
        self.assertEqual(scraper.output_dir, "news_data")
    
    def test_output_dir_created(self):
        """测试输出目录自动创建"""
        # 删除目录后重新初始化
        import shutil
        if os.path.exists("news_data"):
            shutil.rmtree("news_data")
        
        scraper = NewsScraper()
        self.assertTrue(os.path.exists("news_data"))
    
    def test_headers_content(self):
        """测试请求头内容"""
        scraper = NewsScraper()
        self.assertIn('Mozilla', scraper.headers['User-Agent'])
        self.assertIn('application/json', scraper.headers['Accept'])
        self.assertIn('zh-CN', scraper.headers['Accept-Language'])


class TestCheckNetwork(unittest.TestCase):
    """白盒测试：网络检查逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    @patch('news_scraper.requests.get')
    def test_first_url_success(self, mock_get):
        """测试第一个URL成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.scraper.check_network()
        self.assertTrue(result)
        mock_get.assert_called_once()  # 只调用一次
    
    @patch('news_scraper.requests.get')
    def test_second_url_success(self, mock_get):
        """测试第一个失败，第二个成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # 第一次失败，第二次成功
        mock_get.side_effect = [
            Exception("Timeout"),
            mock_response
        ]
        
        result = self.scraper.check_network()
        self.assertTrue(result)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('news_scraper.requests.get')
    def test_all_urls_fail(self, mock_get):
        """测试所有URL都失败"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.scraper.check_network()
        self.assertFalse(result)
    
    @patch('news_scraper.requests.get')
    def test_non_200_status(self, mock_get):
        """测试非200状态码"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.scraper.check_network()
        self.assertFalse(result)


class TestFetchNews(unittest.TestCase):
    """白盒测试：新闻获取逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    @patch('news_scraper.requests.get')
    def test_successful_fetch(self, mock_get):
        """测试成功获取新闻"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'code': '200',
            'data': {
                'list': [
                    {'ctime': str(int(time.time())), 'title': '新闻1', 'digest': '内容1'},
                    {'ctime': str(int(time.time())), 'title': '新闻2', 'digest': '内容2'}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_news(page=1)
        self.assertEqual(len(result), 2)
    
    @patch('news_scraper.requests.get')
    def test_empty_response(self, mock_get):
        """测试空响应"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': '200', 'data': {'list': []}}
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_news(page=1)
        self.assertEqual(result, [])
    
    @patch('news_scraper.requests.get')
    def test_error_code(self, mock_get):
        """测试错误状态码"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': '500', 'data': None}
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_news(page=1)
        self.assertEqual(result, [])
    
    @patch('news_scraper.requests.get')
    def test_missing_data_key(self, mock_get):
        """测试缺少data键"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'code': '200'}
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_news(page=1)
        self.assertEqual(result, [])
    
    @patch('news_scraper.requests.get')
    def test_request_exception(self, mock_get):
        """测试请求异常"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.scraper.fetch_news(page=1)
        self.assertEqual(result, [])


class TestExtractSummary(unittest.TestCase):
    """白盒测试：摘要提取逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_empty_content(self):
        """测试空内容"""
        self.assertEqual(self.scraper.extract_summary(''), '')
        self.assertEqual(self.scraper.extract_summary(None), '')
    
    def test_html_removal(self):
        """测试HTML标签移除"""
        content = '<p>这是<b>测试</b>内容</p>'
        result = self.scraper.extract_summary(content)
        self.assertNotIn('<', result)
        self.assertIn('这是', result)
    
    def test_whitespace_normalization(self):
        """测试空白字符规范化"""
        content = '这是   测试\n\n内容'
        result = self.scraper.extract_summary(content)
        self.assertNotIn('\n', result)
        self.assertNotIn('  ', result)
    
    def test_exact_length(self):
        """测试正好等于最大长度"""
        content = 'a' * 150
        result = self.scraper.extract_summary(content)
        self.assertEqual(len(result), 150)
        self.assertNotIn('...', result)
    
    def test_over_length(self):
        """测试超过最大长度"""
        content = 'a' * 200
        result = self.scraper.extract_summary(content)
        self.assertEqual(len(result), 153)  # 150 + "..."
        self.assertTrue(result.endswith('...'))
    
    def test_under_length(self):
        """测试小于最大长度"""
        content = '短内容'
        result = self.scraper.extract_summary(content)
        self.assertEqual(result, '短内容')
        self.assertNotIn('...', result)
    
    def test_custom_max_length(self):
        """测试自定义最大长度"""
        content = 'a' * 100
        result = self.scraper.extract_summary(content, max_length=50)
        self.assertEqual(len(result), 53)  # 50 + "..."


class TestProcessNewsItem(unittest.TestCase):
    """白盒测试：新闻项处理逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_normal_item(self):
        """测试正常新闻项"""
        timestamp = int(time.time())
        item = {
            'ctime': str(timestamp),
            'title': '测试标题',
            'digest': '<p>测试内容</p>'
        }
        
        result = self.scraper.process_news_item(item)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['标题'], '测试标题')
        self.assertEqual(result['内容详情'], '测试内容')
        self.assertEqual(result['时间戳'], timestamp)
        self.assertIn('时间', result)
        self.assertIn('日期', result)
    
    def test_missing_fields(self):
        """测试缺少字段"""
        item = {}
        result = self.scraper.process_news_item(item)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['标题'], '')
        self.assertEqual(result['内容详情'], '')
        self.assertEqual(result['时间戳'], 0)
    
    def test_invalid_timestamp(self):
        """测试无效时间戳"""
        item = {
            'ctime': 'invalid',
            'title': '标题',
            'digest': '内容'
        }
        
        result = self.scraper.process_news_item(item)
        self.assertIsNone(result)  # 应该返回None
    
    def test_html_cleaning(self):
        """测试HTML清理"""
        item = {
            'ctime': str(int(time.time())),
            'title': '<b>标题</b>',
            'digest': '<p>内容</p><br/>'
        }
        
        result = self.scraper.process_news_item(item)
        # 注意：process_news_item 只清理 digest 中的HTML，不清理 title
        self.assertIn('<', result['标题'])  # title 不清理
        self.assertNotIn('<', result['内容详情'])  # digest 会清理
    
    def test_whitespace_stripping(self):
        """测试空白去除"""
        item = {
            'ctime': str(int(time.time())),
            'title': '  标题  ',
            'digest': '  内容  '
        }
        
        result = self.scraper.process_news_item(item)
        self.assertEqual(result['标题'], '标题')
        self.assertEqual(result['内容详情'], '内容')


class TestFilterPerformanceNews(unittest.TestCase):
    """白盒测试：业绩公告筛选逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_match_performance_keywords(self):
        """测试匹配业绩关键词"""
        news_list = [
            {'标题': '业绩增长', '内容详情': '内容', '时间戳': 1},
            {'标题': '净利润', '内容详情': '内容', '时间戳': 2},
            {'标题': '营收', '内容详情': '内容', '时间戳': 3},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 3)
    
    def test_exclude_st_keywords(self):
        """测试排除ST关键词"""
        news_list = [
            {'标题': '业绩增长', '内容详情': 'ST公司', '时间戳': 1},
            {'标题': '*ST公司', '内容详情': '净利润', '时间戳': 2},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 0)
    
    def test_exclude_loss_keywords(self):
        """测试排除亏损关键词"""
        news_list = [
            {'标题': '业绩', '内容详情': '亏损', '时间戳': 1},
            {'标题': '业绩', '内容详情': '同比下滑', '时间戳': 2},
            {'标题': '业绩', '内容详情': '预亏', '时间戳': 3},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 0)
    
    def test_no_keywords(self):
        """测试无关键词"""
        news_list = [
            {'标题': '普通新闻', '内容详情': '内容', '时间戳': 1},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 0)
    
    def test_title_and_content_match(self):
        """测试标题和内容都匹配"""
        news_list = [
            {'标题': '业绩', '内容详情': '净利润增长', '时间戳': 1},
        ]
        
        result = self.scraper.filter_performance_news(news_list)
        self.assertEqual(len(result), 1)


class TestFilterPolicyBenefits(unittest.TestCase):
    """白盒测试：政策利好筛选逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_match_policy_keywords(self):
        """测试匹配政策关键词"""
        news_list = [
            {'标题': '政策支持', '内容详情': '内容', '时间戳': 1},
            {'标题': '利好', '内容详情': '内容', '时间戳': 2},
            {'标题': '鼓励发展', '内容详情': '内容', '时间戳': 3},
        ]
        
        result = self.scraper.filter_policy_benefits(news_list)
        self.assertEqual(len(result), 3)
    
    def test_exclude_stock_codes(self):
        """测试排除股票代码"""
        news_list = [
            {'标题': '政策利好', '内容详情': '600000公司', '时间戳': 1},
            {'标题': '政策利好', '内容详情': '000001公司', '时间戳': 2},
            {'标题': '政策利好', '内容详情': '300001公司', '时间戳': 3},
        ]
        
        result = self.scraper.filter_policy_benefits(news_list)
        self.assertEqual(len(result), 0)
    
    def test_exclude_single_stock_keywords(self):
        """测试排除单只股票特征词"""
        news_list = [
            {'标题': '政策', '内容详情': '公告 披露 审议 通过', '时间戳': 1},  # 4个特征词
            {'标题': '政策', '内容详情': '公告 披露 审议', '时间戳': 2},  # 3个特征词
            {'标题': '政策', '内容详情': '公告 披露', '时间戳': 3},  # 2个特征词，应该保留
        ]
        
        result = self.scraper.filter_policy_benefits(news_list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['时间戳'], 3)
    
    def test_no_policy_keywords(self):
        """测试无政策关键词"""
        news_list = [
            {'标题': '普通新闻', '内容详情': '内容', '时间戳': 1},
        ]
        
        result = self.scraper.filter_policy_benefits(news_list)
        self.assertEqual(len(result), 0)


class TestAnalyzeNewsStocks(unittest.TestCase):
    """白盒测试：新闻分析股票逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
        # Mock _get_industry_stocks to avoid network requests
        self.mock_get_stocks = patch.object(
            self.scraper, '_get_industry_stocks',
            return_value={
                'matched': True,
                'type': '行业',
                'name': '测试行业',
                'stocks': [{'代码': '600000', '名称': '测试股票'}],
                'count': 1
            }
        )
        self.mock_get_stocks.start()
    
    def tearDown(self):
        self.mock_get_stocks.stop()
    
    def test_exact_match(self):
        """测试精确匹配行业"""
        title = "光伏"
        content = "光伏产业发展"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('光伏', industry_names)
    
    def test_partial_match(self):
        """测试部分匹配"""
        title = "新能源汽车"
        content = "内容"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
    
    def test_new_energy_vehicle_special_handling(self):
        """测试新能源汽车特殊处理"""
        title = "新能源汽车"
        content = "产业发展"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        # 应包含新能源车
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('新能源车', industry_names)
    
    def test_finance_subsector_expansion(self):
        """测试金融子板块展开"""
        title = "金融"
        content = "改革"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        # 应包含所有金融子板块
        self.assertIn('银行', industry_names)
        self.assertIn('证券', industry_names)
        self.assertIn('保险', industry_names)
    
    def test_finance_subsector_no_expansion_when_specific(self):
        """测试提到具体子板块时不展开"""
        title = "银行"
        content = "改革"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('银行', industry_names)
        # 不应包含证券、保险
        self.assertNotIn('证券', industry_names)
        self.assertNotIn('保险', industry_names)
    
    def test_no_match(self):
        """测试无匹配"""
        title = "天气"
        content = "晴朗"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertFalse(result['matched'])
        self.assertEqual(result['stocks'], [])
        self.assertEqual(result['industries'], [])
    
    def test_multiple_industries(self):
        """测试多行业匹配"""
        title = "光伏和风电"
        content = "新能源发展"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        self.assertTrue(len(result['industries']) >= 2)
    
    def test_longer_keyword_priority(self):
        """测试长关键词优先"""
        title = "新能源车"
        content = "内容"
        
        result = self.scraper.analyze_news_stocks(title, content)
        self.assertTrue(result['matched'])
        # 应匹配新能源车而不是汽车
        industry_names = [ind['name'] for ind in result['industries']]
        self.assertIn('新能源车', industry_names)
    
    def test_empty_input(self):
        """测试空输入"""
        result = self.scraper.analyze_news_stocks('', '')
        self.assertFalse(result['matched'])
    
    def test_none_input(self):
        """测试None输入"""
        result = self.scraper.analyze_news_stocks(None, None)
        self.assertFalse(result['matched'])


class TestAnalyzePolicyStocks(unittest.TestCase):
    """白盒测试：政策分析股票逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
        # Mock methods to avoid network requests
        self.mock_get_stocks = patch.object(
            self.scraper, '_get_industry_stocks',
            return_value={
                'matched': True,
                'type': '行业',
                'name': '测试行业',
                'stocks': [{'代码': '600000', '名称': '测试股票'}],
                'count': 1
            }
        )
        self.mock_get_stocks.start()
        
        self.mock_province_stocks = patch.object(
            self.scraper, '_get_province_stocks',
            return_value={
                'matched': True,
                'type': '地区',
                'name': '黑龙江',
                'stocks': [{'代码': '600000', '名称': '测试股票'}],
                'count': 1
            }
        )
        self.mock_province_stocks.start()
        
        self.mock_all_a_stocks = patch.object(
            self.scraper, '_get_all_a_stocks',
            return_value={
                'matched': True,
                'type': '全部A股',
                'stocks': [{'代码': '600000', '名称': '测试股票'}],
                'count': 1
            }
        )
        self.mock_all_a_stocks.start()
    
    def tearDown(self):
        self.mock_get_stocks.stop()
        self.mock_province_stocks.stop()
        self.mock_all_a_stocks.stop()
    
    def test_national_policy_detection(self):
        """测试国家政策检测"""
        policy = "国家支持新能源汽车发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        self.assertEqual(result['type'], '国家政策')
    
    def test_local_policy_detection(self):
        """测试地方政策检测"""
        policy = "黑龙江省支持机器人产业发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
        self.assertEqual(result['type'], '地方政策')
        self.assertEqual(result['region'], '黑龙江')
    
    def test_dict_input(self):
        """测试字典输入"""
        policy = {
            '标题': '国家支持新能源',
            '内容详情': '政策内容'
        }
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
    
    def test_only_region_match(self):
        """测试只匹配地区"""
        policy = "黑龙江省经济发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
    
    def test_only_industry_match(self):
        """测试只匹配行业"""
        policy = "支持新能源产业发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertTrue(result['matched'])
    
    def test_no_match(self):
        """测试无匹配"""
        policy = "今天天气很好"
        
        result = self.scraper.analyze_policy_stocks(policy)
        self.assertFalse(result['matched'])
    
    def test_national_policy_all_stocks(self):
        """测试国家政策返回全部A股"""
        policy = "国家支持经济发展"
        
        result = self.scraper.analyze_policy_stocks(policy)
        # 国家政策无具体行业时应返回全部A股
        self.assertTrue(result['matched'])
        self.assertEqual(result['type'], '全部A股')


class TestGetIndustryStocks(unittest.TestCase):
    """白盒测试：获取行业股票逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    @patch('news_scraper.requests.get')
    def test_successful_parse(self, mock_get):
        """测试成功解析"""
        mock_response = MagicMock()
        mock_response.text = 'var data = {"block":{"items":[{"5":"600000","55":"测试","199112":"1.0","10":"10.0","13":"100"}]}};'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = self.scraper._get_industry_stocks('测试', '881111')
        self.assertTrue(result['matched'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['stocks'][0]['代码'], '600000')
        self.assertEqual(result['stocks'][0]['名称'], '测试')
    
    @patch('news_scraper.requests.get')
    def test_st_filtering(self, mock_get):
        """测试ST股票过滤"""
        mock_response = MagicMock()
        mock_response.text = 'var data = {"block":{"items":[{"5":"600000","55":"ST测试","199112":"1.0","10":"10.0","13":"100"},{"5":"600001","55":"*ST测试","199112":"1.0","10":"10.0","13":"100"},{"5":"600002","55":"正常","199112":"1.0","10":"10.0","13":"100"}]}};'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = self.scraper._get_industry_stocks('测试', '881111')
        self.assertTrue(result['matched'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['stocks'][0]['名称'], '正常')
    
    @patch('news_scraper.requests.get')
    def test_missing_columns(self, mock_get):
        """测试缺少必要列"""
        mock_response = MagicMock()
        mock_response.text = 'var data = {"block":{"items":[{"1":"600000","2":"测试"}]}};'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = self.scraper._get_industry_stocks('测试', '881111')
        self.assertFalse(result['matched'])
    
    @patch('news_scraper.requests.get')
    def test_request_exception(self, mock_get):
        """测试请求异常"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.scraper._get_industry_stocks('测试', '881111')
        self.assertFalse(result['matched'])
        self.assertIn('message', result)


class TestProvinceStocks(unittest.TestCase):
    """白盒测试：地区股票逻辑"""
    
    def setUp(self):
        self.scraper = NewsScraper()
    
    def test_province_map_completeness(self):
        """测试地区映射完整性"""
        required_provinces = [
            '北京', '上海', '广东', '深圳', '浙江', '江苏', '四川', '重庆',
            '湖北', '湖南', '河南', '河北', '山东', '山西', '安徽', '福建',
            '江西', '辽宁', '吉林', '黑龙江', '陕西', '甘肃', '青海',
            '云南', '贵州', '海南', '内蒙古', '新疆', '西藏', '广西',
            '宁夏', '天津', '浦东'
        ]
        
        for province in required_provinces:
            self.assertIn(province, PROVINCE_MAP)
    
    def test_province_code_format(self):
        """测试地区代码格式"""
        for province, code in PROVINCE_MAP.items():
            self.assertTrue(code.startswith('882'), f"{province}: {code}")
            self.assertEqual(len(code), 6, f"{province}: {code}")
    
    def test_province_code_uniqueness(self):
        """测试地区代码唯一性"""
        codes = list(PROVINCE_MAP.values())
        self.assertEqual(len(codes), len(set(codes)))


class TestCloseExcelFile(unittest.TestCase):
    """白盒测试：关闭Excel文件逻辑"""
    
    def test_nonexistent_file(self):
        """测试不存在的文件"""
        result = close_excel_file('nonexistent.xlsx')
        self.assertFalse(result)
    
    def test_file_openable(self):
        """测试文件可打开（非Excel文件）"""
        # 创建一个普通文本文件
        with open('test.txt', 'w') as f:
            f.write('test')
        
        result = close_excel_file('test.txt')
        self.assertFalse(result)  # 不是Excel文件，应该返回False
        
        # 清理
        if os.path.exists('test.txt'):
            os.remove('test.txt')
    
    def test_com_import_inside_function(self):
        """测试COM导入在函数内部"""
        # 验证 close_excel_file 函数内部导入 win32com
        import inspect
        source = inspect.getsource(close_excel_file)
        self.assertIn('import win32com', source)
        self.assertIn('import pythoncom', source)


class TestSaveExcelWithRetry(unittest.TestCase):
    """白盒测试：带重试的Excel保存逻辑"""
    
    def setUp(self):
        self.test_dir = "test_excel_whitebox"
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        import shutil
        import time
        if os.path.exists(self.test_dir):
            time.sleep(1)
            try:
                shutil.rmtree(self.test_dir)
            except:
                pass
    
    def test_single_sheet_success(self):
        """测试单sheet成功保存"""
        df = pd.DataFrame({'A': [1]})
        filepath = os.path.join(self.test_dir, 'test.xlsx')
        
        result = save_excel_with_retry(df, filepath)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filepath))
    
    def test_multiple_sheets_success(self):
        """测试多sheet成功保存"""
        df1 = pd.DataFrame({'A': [1]})
        df2 = pd.DataFrame({'B': [2]})
        filepath = os.path.join(self.test_dir, 'test.xlsx')
        
        result = save_excel_with_retry({'sheet1': df1, 'sheet2': df2}, filepath)
        self.assertTrue(result)
        
        xl = pd.ExcelFile(filepath)
        self.assertEqual(len(xl.sheet_names), 2)
        xl.close()
    
    def test_invalid_path(self):
        """测试无效路径"""
        df = pd.DataFrame({'A': [1]})
        result = save_excel_with_retry(df, '/invalid/path/test.xlsx')
        self.assertFalse(result)
    
    def test_overwrite_existing(self):
        """测试覆盖已存在文件"""
        df1 = pd.DataFrame({'A': [1]})
        df2 = pd.DataFrame({'A': [2]})
        filepath = os.path.join(self.test_dir, 'test.xlsx')
        
        save_excel_with_retry(df1, filepath)
        result = save_excel_with_retry(df2, filepath)
        
        self.assertTrue(result)
        df_read = pd.read_excel(filepath)
        self.assertEqual(df_read['A'].iloc[0], 2)


def run_tests():
    """运行所有白盒测试"""
    print("=" * 60)
    print("同花顺7*24快讯抓取工具 - 白盒测试")
    print("=" * 60)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestNewsScraperInit,
        TestCheckNetwork,
        TestFetchNews,
        TestExtractSummary,
        TestProcessNewsItem,
        TestFilterPerformanceNews,
        TestFilterPolicyBenefits,
        TestAnalyzeNewsStocks,
        TestAnalyzePolicyStocks,
        TestGetIndustryStocks,
        TestProvinceStocks,
        TestCloseExcelFile,
        TestSaveExcelWithRetry,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("白盒测试结果摘要")
    print("=" * 60)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("所有白盒测试通过！")
    else:
        print("部分测试失败，请检查错误信息")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
