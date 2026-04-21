import requests
import json
import time
import schedule
import os
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import re
from concept_codes import concept_map
from keywords import (
    PERFORMANCE_KEYWORDS, EXCLUDE_KEYWORDS, POLICY_KEYWORDS,
    SINGLE_STOCK_KEYWORDS, NATIONAL_KEYWORDS, PROVINCE_MAP,
    FINANCE_SUBSECTORS, FINANCE_EXCLUDE_KEYWORDS,
    NEW_ENERGY_SUBSECTORS, NEW_ENERGY_EXCLUDE_KEYWORDS,
    REAL_ESTATE_SUBSECTORS, REAL_ESTATE_EXCLUDE_KEYWORDS,
    MEDICINE_SUBSECTORS, MEDICINE_EXCLUDE_KEYWORDS,
    FTZ_SUBSECTORS, FTZ_EXCLUDE_KEYWORDS
)

def close_excel_file(filepath):
    """尝试关闭正在打开的Excel文件（Windows）"""
    try:
        import win32com.client
        import pythoncom
        
        # 初始化COM
        pythoncom.CoInitialize()
        
        # 获取Excel应用程序
        excel = win32com.client.Dispatch("Excel.Application")
        
        # 遍历所有打开的工作簿
        for workbook in excel.Workbooks:
            if os.path.abspath(workbook.FullName) == os.path.abspath(filepath):
                print(f"检测到文件被打开: {os.path.basename(filepath)}，正在关闭...")
                workbook.Close(SaveChanges=False)
                time.sleep(0.5)
                pythoncom.CoUninitialize()
                return True
        
        pythoncom.CoUninitialize()
        return False
    except Exception:
        # 如果COM方式失败，尝试其他方法
        try:
            # 检查文件是否被占用
            with open(filepath, 'r+') as f:
                return False  # 文件未被占用
        except PermissionError:
            # 文件被占用，但无法通过COM关闭
            print(f"警告: 文件 {os.path.basename(filepath)} 正在被使用，请手动关闭后重试")
            return False


def save_excel_with_retry(df, filepath, sheet_name='Sheet1', max_retries=3):
    """保存Excel文件，自动处理文件被占用的情况"""
    # 如果文件存在且被占用，尝试关闭
    if os.path.exists(filepath):
        close_excel_file(filepath)
    
    for attempt in range(max_retries):
        try:
            if isinstance(df, dict):
                # 多个sheet
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    for name, data in df.items():
                        data.to_excel(writer, sheet_name=name, index=False)
            else:
                # 单个sheet
                df.to_excel(filepath, index=False, engine='openpyxl')
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"文件被占用，尝试关闭Excel文件... ({attempt + 1}/{max_retries})")
                close_excel_file(filepath)
                time.sleep(1)
            else:
                print(f"错误: 无法保存文件 {os.path.basename(filepath)}，请手动关闭Excel后重试")
                return False
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            return False
    
    return False

class NewsScraper:
    def __init__(self):
        self.base_url = "https://www.10jqka.com.cn/"
        self.api_url = "https://news.10jqka.com.cn/tapp/news/push/stock/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.10jqka.com.cn/',
        }
        self.news_data = {}
        self.output_dir = "news_data"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def check_network(self):
        """检查网络连接是否正常"""
        try:
            test_urls = [
                'https://www.baidu.com',
                'https://www.10jqka.com.cn'
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"网络检查异常: {e}")
            return False
        
    def fetch_news(self, page=1):
        """获取7*24快讯数据"""
        try:
            params = {
                'page': page,
                'tag': '',
                'track': 'website',
                'field': 'time',
                'order': 'desc',
                'type': '1',
            }
            
            response = requests.get(self.api_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == '200' and data.get('data') and data['data'].get('list'):
                return data['data']['list']
            return []
        except Exception as e:
            print(f"获取新闻数据失败: {e}")
            return []
    
    def extract_summary(self, content, max_length=150):
        """提取内容摘要"""
        if not content:
            return ""
        
        # 移除HTML标签
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余空白
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # 截取指定长度
        if len(clean_content) > max_length:
            return clean_content[:max_length] + "..."
        return clean_content
    
    def process_news_item(self, item):
        """处理单条新闻数据"""
        try:
            timestamp = int(item.get('ctime', 0))
            news_time = datetime.fromtimestamp(timestamp)
            
            title = item.get('title', '').strip()
            digest = item.get('digest', '').strip()
            
            # 移除HTML标签
            clean_content = re.sub(r'<[^>]+>', '', digest)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            return {
                '时间': news_time.strftime('%Y-%m-%d %H:%M:%S'),
                '标题': title,
                '内容详情': clean_content,
                '日期': news_time.strftime('%Y-%m-%d'),
                '时间戳': timestamp
            }
        except Exception as e:
            print(f"处理新闻项失败: {e}")
            return None
    
    def fetch_today_news(self, max_pages=50):
        """获取当天的新闻数据"""
        all_news = []
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        for page in range(1, max_pages + 1):
            news_items = self.fetch_news(page)
            if not news_items:
                break
            
            # 显示进度
            if page % 10 == 0:
                print(f"已获取 {page} 页数据...")
                
            for item in news_items:
                processed = self.process_news_item(item)
                if processed:
                    # 只保留当天的数据
                    if processed['日期'] == today_str:
                        all_news.append(processed)
                    else:
                        # 非当天数据，停止获取
                        return all_news
            
            time.sleep(0.3)
        
        return all_news
    
    def fetch_specific_date_news(self, date_str, max_pages=200):
        """获取指定日期的新闻数据"""
        all_news = []
        
        for page in range(1, max_pages + 1):
            news_items = self.fetch_news(page)
            if not news_items:
                break
            
            # 显示进度
            if page % 10 == 0:
                print(f"已获取 {page} 页数据...")
                
            for item in news_items:
                processed = self.process_news_item(item)
                if processed:
                    # 只保留指定日期的数据
                    if processed['日期'] == date_str:
                        all_news.append(processed)
                    elif processed['日期'] < date_str:
                        # 早于指定日期，停止获取
                        return all_news
            
            time.sleep(0.3)
        
        return all_news
    
    def filter_performance_news(self, news_list):
        """筛选业绩公告相关的新闻，过滤ST股票和业绩亏损"""
        keywords = PERFORMANCE_KEYWORDS
        exclude_keywords = EXCLUDE_KEYWORDS
        
        filtered = []
        for news in news_list:
            title = news.get('标题', '')
            content = news.get('内容详情', '')
            
            # 检查是否包含业绩关键词
            if not any(keyword in title or keyword in content for keyword in keywords):
                continue
            
            # 检查是否包含ST或亏损关键词，如果包含则跳过
            if any(keyword in title or keyword in content for keyword in exclude_keywords):
                continue
            
            filtered.append(news)
        
        return filtered
    
    def filter_performance_stocks_by_price(self, news_list, min_price=3, max_price=50):
        """筛选业绩公告中价格在指定范围的股票
        
        从标题中截取"："之前的文字作为股票名称，
        到同花顺下载对应的股票代码和名称映射，
        找到当天价格进行判断，筛选价格在min_price到max_price之间的股票
        
        Args:
            news_list: 新闻列表
            min_price: 最低价格（默认3元）
            max_price: 最高价格（默认50元）
            
        Returns:
            list: 符合条件的股票信息列表
        """
        try:
            # 获取全部A股列表（用于股票名称到代码的映射）
            all_stocks_result = self._get_all_a_stocks()
            if not all_stocks_result.get('matched'):
                print("获取A股列表失败")
                return []
            
            # 创建股票名称到信息的映射
            stock_name_map = {}
            for stock in all_stocks_result['stocks']:
                name = stock['名称']
                code = stock['代码']
                # 只保留A股（60/00/30开头），排除科创板（688开头）和ST股票
                if code.startswith(('60', '00', '30')) and 'ST' not in name:
                    stock_name_map[name] = stock
            
            filtered_stocks = []
            seen_codes = set()  # 用于去重
            
            for news in news_list:
                title = news.get('标题', '')
                
                # 从标题中提取股票名称（"："之前的文字）
                stock_name = None
                if '：' in title:
                    stock_name = title.split('：')[0].strip()
                elif ':' in title:
                    stock_name = title.split(':')[0].strip()
                
                if not stock_name:
                    continue
                
                # 在股票映射中查找
                if stock_name in stock_name_map:
                    stock_info = stock_name_map[stock_name]
                    code = stock_info['代码']
                    
                    # 去重
                    if code in seen_codes:
                        continue
                    
                    # 获取价格并判断
                    price_str = stock_info.get('价格', '')
                    try:
                        price = float(price_str)
                        if price > min_price and price <= max_price:
                            seen_codes.add(code)
                            filtered_stocks.append({
                                '代码': code,
                                '名称': stock_name,
                                '价格': price,
                                '涨跌幅': stock_info.get('涨跌幅', ''),
                                '新闻标题': title,
                                '新闻时间': news.get('时间', ''),
                            })
                    except (ValueError, TypeError):
                        # 价格无法转换为数字，跳过
                        continue
            
            return filtered_stocks
        except Exception as e:
            print(f"筛选业绩股票失败: {e}")
            return []
    
    def filter_policy_benefits(self, news_list):
        """筛选政策利好行业信息，排除单只股票信息"""
        import re
        
        keywords = POLICY_KEYWORDS
        single_stock_keywords = SINGLE_STOCK_KEYWORDS
        
        # 股票代码模式
        stock_code_pattern = re.compile(r'\d{6}')
        
        filtered = []
        for news in news_list:
            title = news.get('标题', '')
            content = news.get('内容详情', '')
            text = title + ' ' + content
            
            # 检查是否包含政策利好关键词
            if not any(keyword in text for keyword in keywords):
                continue
            
            # 排除单只股票信息
            # 1. 检查是否包含股票代码
            codes = stock_code_pattern.findall(text)
            valid_codes = [c for c in codes if c.startswith(('60', '00', '30', '68', '83', '87', '43'))]
            if valid_codes:
                continue
            
            # 2. 检查是否包含大量单只股票特征词（超过3个则认为是单只股票公告）
            stock_keyword_count = sum(1 for kw in single_stock_keywords if kw in text)
            if stock_keyword_count >= 3:
                continue
            
            filtered.append(news)
        
        return filtered
    
    def save_performance_excel(self, news_list, date_str):
        """保存业绩公告到Excel，包含政策利好sheet和业绩股票sheet"""
        if not news_list:
            print(f"{date_str} 无业绩公告数据")
            return
        
        # 按时间排序
        news_list.sort(key=lambda x: x['时间戳'], reverse=True)
        
        # 筛选政策利好信息
        policy_news = self.filter_policy_benefits(news_list)
        
        # 从业绩公告中排除政策利好信息
        policy_timestamps = set(n['时间戳'] for n in policy_news)
        stock_news = [n for n in news_list if n['时间戳'] not in policy_timestamps]
        
        # 业绩公告中保留包含"公告"或"营收"二字的信息
        has_announcement = []
        no_announcement = []
        for news in stock_news:
            title = news.get('标题', '')
            content = news.get('内容详情', '')
            text = title + ' ' + content
            if '公告' in text or '营收' in text:
                has_announcement.append(news)
            else:
                no_announcement.append(news)
        
        # 将不包含"公告"和"营收"的信息加入政策利好
        policy_news.extend(no_announcement)
        
        # 创建DataFrame
        if has_announcement:
            stock_df = pd.DataFrame(has_announcement)
            for col in ['时间', '标题', '内容详情']:
                if col not in stock_df.columns:
                    stock_df[col] = ''
            stock_df = stock_df[['时间', '标题', '内容详情']]
        else:
            stock_df = pd.DataFrame({'时间': [], '标题': [], '内容详情': []})
        
        # 生成文件名（与当天文件对应）
        filename = f"news业绩_{date_str}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # 准备多个sheet的数据
        sheets = {'业绩公告': stock_df}
        
        # 保存政策利好信息到第二个sheet
        if policy_news:
            policy_df = pd.DataFrame(policy_news)
            for col in ['时间', '标题', '内容详情']:
                if col not in policy_df.columns:
                    policy_df[col] = ''
            policy_df = policy_df[['时间', '标题', '内容详情']]
            sheets['政策利好'] = policy_df
            print(f"已保存 {len(news_list)} 条业绩公告到 {filepath}（{len(has_announcement)} 条股票公告 + {len(policy_news)} 条政策利好）")
        else:
            # 如果没有政策利好，创建一个空的sheet
            sheets['政策利好'] = pd.DataFrame({'提示': ['当日无政策利好信息']})
            print(f"已保存 {len(news_list)} 条业绩公告到 {filepath}（无政策利好）")
        
        # 筛选价格在3-50元的业绩股票，保存到第三个sheet
        performance_stocks = self.filter_performance_stocks_by_price(news_list, min_price=3, max_price=50)
        if performance_stocks:
            # 按价格从高到低排序
            performance_stocks.sort(key=lambda x: x['价格'], reverse=True)
            stocks_df = pd.DataFrame(performance_stocks)
            stocks_df = stocks_df[['代码', '名称', '价格', '涨跌幅', '新闻标题', '新闻时间']]
            sheets['业绩股票(3-50元)'] = stocks_df
            print(f"已筛选 {len(performance_stocks)} 条业绩股票（价格3-50元）")
        else:
            sheets['业绩股票(3-50元)'] = pd.DataFrame({'提示': ['当日无符合条件的业绩股票']})
        
        # 使用带重试的保存方法
        save_excel_with_retry(sheets, filepath)
    
    def save_today_excel(self, news_list, date_str):
        """保存当天的新闻到Excel"""
        if not news_list:
            print(f"{date_str} 无新闻数据")
            return
        
        # 按时间排序
        news_list.sort(key=lambda x: x['时间戳'], reverse=True)
        
        # 创建DataFrame
        df = pd.DataFrame(news_list)
        
        # 确保必要的列存在
        required_cols = ['时间', '标题', '内容详情']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
        
        df = df[required_cols]
        
        # 生成文件名
        filename = f"news快讯_{date_str}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # 如果文件已存在，读取现有sheet
        if os.path.exists(filepath):
            try:
                existing_data = pd.read_excel(filepath, sheet_name=None)
                existing_data['7x24快讯'] = df
                
                if save_excel_with_retry(existing_data, filepath):
                    print(f"已保存 {len(news_list)} 条新闻到 {filepath} (7x24快讯sheet)")
            except Exception as e:
                print(f"读取现有文件失败: {e}")
                if save_excel_with_retry({'7x24快讯': df}, filepath):
                    print(f"已保存 {len(news_list)} 条新闻到 {filepath} (7x24快讯sheet)")
        else:
            if save_excel_with_retry({'7x24快讯': df}, filepath):
                print(f"已保存 {len(news_list)} 条新闻到 {filepath} (7x24快讯sheet)")
        
        # 筛选并保存业绩公告
        performance_news = self.filter_performance_news(news_list)
        self.save_performance_excel(performance_news, date_str)
    
    def fetch_cpo_concept_stocks(self):
        """获取CPO概念股票数据"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://q.10jqka.com.cn/',
            }
            
            # CPO概念代码
            cpo_code = '886033'
            
            # 获取CPO概念股票数据
            url = f'https://d.10jqka.com.cn/v2/blockrank/{cpo_code}/199112/d10000.js'
            resp = requests.get(url, headers=headers, timeout=10)
            text = resp.text[:-1]
            text = text.split('{"block":')[-1]
            text = '{"block":' + text
            text = text.replace('null', 'None')
            data = eval(text)
            
            items = data.get('items', [])
            df = pd.DataFrame(items)
            
            # 列名映射
            col_mapping = {
                "5": "代码",
                "55": "名称", 
                "199112": "涨跌幅",
                "10": "价格",
                "13": "成交量"
            }
            
            existing_mapping = {k: v for k, v in col_mapping.items() if k in df.columns}
            df.rename(columns=existing_mapping, inplace=True)
            
            # 剔除ST股票
            if '名称' in df.columns:
                df = df[~df['名称'].str.contains('ST', na=False)]
            
            print(f'共获取到 {len(df)} 只CPO概念股')
            
            # 根据股票名称和业务范围进行分类
            categories = {
                '光芯片': ['芯', '激光', '光电', '光子', '半导体'],
                'CPO封装': ['封装', '精密', '科技', '电子', '材料'],
                'MPO连接器': ['连接', '通信', '信息', '线缆', '光纤'],
                '光模块设备': ['模块', '设备', '仪器', '技术', '制造'],
                '光模块': ['光', '通信', '科技', '网络', '系统'],
            }
            
            # 初始化分类字典
            category_stocks = {name: [] for name in categories.keys()}
            category_stocks['全部'] = df.to_dict('records')
            
            # 对每只股票进行分类
            for _, row in df.iterrows():
                name = row.get('名称', '')
                
                # 检查每个分类
                for category, keywords in categories.items():
                    if any(kw in name for kw in keywords):
                        category_stocks[category].append(row.to_dict())
            
            # 打印分类结果
            for category, stocks in category_stocks.items():
                print(f'{category}: {len(stocks)} 只股票')
            
            # 创建Excel文件
            date_str = datetime.now().strftime('%Y-%m-%d')
            filepath = os.path.join(self.output_dir, f'CPO概念_{date_str}.xlsx')
            
            # 准备sheet数据
            sheets = {}
            for category, stocks in category_stocks.items():
                if stocks:
                    sheets[category] = pd.DataFrame(stocks)
            
            # 保存到Excel
            save_excel_with_retry(sheets, filepath)
            print(f'已保存到 {filepath}')
            
            return True
        except Exception as e:
            print(f'获取CPO概念数据失败: {e}')
            import traceback
            traceback.print_exc()
            return False

    def run_fetch(self):
        """执行一次抓取任务"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取新闻数据...")
        
        # 检查网络连接
        if not self.check_network():
            print("网络连接异常，跳过本次抓取")
            return
        
        print("网络连接正常，开始抓取...")
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        news_list = self.fetch_today_news()
        
        if news_list:
            # 保存到内存中
            if today_str not in self.news_data:
                self.news_data[today_str] = []
            
            # 检查是否已存在
            existing_timestamps = [n['时间戳'] for n in self.news_data[today_str]]
            new_count = 0
            for news in news_list:
                if news['时间戳'] not in existing_timestamps:
                    self.news_data[today_str].append(news)
                    new_count += 1
            
            # 保存当天的数据
            self.save_today_excel(self.news_data[today_str], today_str)
            print(f"本次抓取到 {len(news_list)} 条新闻，新增 {new_count} 条")
        else:
            print("未获取到新闻数据")
    
    def fetch_and_save_specific_date(self, date_str):
        """获取并保存指定日期的新闻数据"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取 {date_str} 新闻数据...")
        
        # 检查网络连接
        if not self.check_network():
            print("网络连接异常，跳过本次抓取")
            return
        
        print("网络连接正常，开始抓取...")
        
        news_list = self.fetch_specific_date_news(date_str)
        
        if news_list:
            # 保存到内存中
            if date_str not in self.news_data:
                self.news_data[date_str] = []
            
            # 检查是否已存在
            existing_timestamps = [n['时间戳'] for n in self.news_data[date_str]]
            new_count = 0
            for news in news_list:
                if news['时间戳'] not in existing_timestamps:
                    self.news_data[date_str].append(news)
                    new_count += 1
            
            # 保存数据
            self.save_today_excel(self.news_data[date_str], date_str)
            
            # 保存头条新闻
            self.save_headline_news(date_str)
            
            print(f"本次抓取到 {len(news_list)} 条新闻，新增 {new_count} 条")
        else:
            print(f"未获取到 {date_str} 的新闻数据")
    
    def analyze_news_stocks(self, title, content):
        """根据新闻标题和内容分析利好行业板块，并找出相关股票"""
        import re
        
        # 使用已验证有效的概念板块代码映射
        industry_map = concept_map.copy()
        
        # 添加 concept_map 中没有的行业代码
        industry_map.update({
            '非金属': '881115',
            '机械': '881117',
        })
        
        text = (title or '') + ' ' + (content or '')
        
        # 查找所有匹配的行业（按关键词长度排序，优先匹配长关键词）
        sorted_industries = sorted(industry_map.keys(), key=len, reverse=True)
        matched_industries = []
        matched_keywords = []
        
        for ind in sorted_industries:
            if ind in text:
                # 避免重复匹配（如"新能源"和"新能源车"都匹配时，保留更具体的）
                is_sub = False
                for existing in matched_keywords:
                    if ind in existing or existing in ind:
                        if len(ind) < len(existing):
                            is_sub = True
                            break
                if not is_sub:
                    # 移除已被包含的短关键词
                    matched_keywords = [k for k in matched_keywords if len(k) < len(ind) or ind not in k]
                    matched_keywords.append(ind)
                    matched_industries.append((ind, industry_map[ind]))
        
        # 特殊处理："新能源汽车" 等同于 "新能源车"
        if '新能源汽车' in text and '新能源车' not in matched_keywords:
            matched_keywords.append('新能源车')
            matched_industries.append(('新能源车', '881125'))
        
        # 综合板块处理：当提到综合板块但没提到具体子板块时，添加所有子板块
        subsector_configs = [
            ('新能源', NEW_ENERGY_SUBSECTORS, NEW_ENERGY_EXCLUDE_KEYWORDS),
            ('金融', FINANCE_SUBSECTORS, FINANCE_EXCLUDE_KEYWORDS),
            ('房地产', REAL_ESTATE_SUBSECTORS, REAL_ESTATE_EXCLUDE_KEYWORDS),
            ('医药', MEDICINE_SUBSECTORS, MEDICINE_EXCLUDE_KEYWORDS),
            ('自贸区', FTZ_SUBSECTORS, FTZ_EXCLUDE_KEYWORDS),
        ]
        
        for parent_name, subsectors, exclude_kw in subsector_configs:
            if parent_name in text and not any(kw in text for kw in exclude_kw):
                for sub_name, sub_code in subsectors:
                    matched_industries.append((sub_name, sub_code))
        
        if not matched_industries:
            return {'matched': False, 'message': '未能识别相关行业或板块', 'stocks': [], 'industries': []}
        
        # 获取所有匹配行业的股票并合并
        all_stocks = []
        industry_results = []
        
        for ind_name, ind_code in matched_industries:
            result = self._get_industry_stocks(ind_name, ind_code)
            if result.get('matched'):
                industry_results.append({
                    'name': ind_name,
                    'code': ind_code,
                    'count': len(result['stocks'])
                })
                all_stocks.extend(result['stocks'])
        
        # 去重（按股票代码）
        seen_codes = set()
        unique_stocks = []
        for stock in all_stocks:
            if stock['代码'] not in seen_codes:
                seen_codes.add(stock['代码'])
                unique_stocks.append(stock)
        
        return {
            'matched': True,
            'type': '新闻分析',
            'name': '_'.join([ind['name'] for ind in industry_results]),
            'stocks': unique_stocks,
            'count': len(unique_stocks),
            'industries': industry_results
        }
    
    def analyze_policy_stocks(self, policy_text):
        """分析政策利好信息，找出相关受益股票"""
        import re
        
        # 使用已验证有效的概念板块代码映射
        industry_map = concept_map.copy()
        
        # 添加 concept_map 中没有的行业代码
        industry_map.update({
            '非金属': '881115',
            '机械': '881117',
        })
        
        # 地区关键词
        province_map = PROVINCE_MAP
        provinces = list(province_map.keys())
        
        # 国家政策关键词
        national_keywords = NATIONAL_KEYWORDS
        
        text = policy_text
        title = ''
        if isinstance(policy_text, dict):
            title = policy_text.get('标题', '')
            text = title + ' ' + policy_text.get('内容详情', '')
        
        # 判断是国家政策还是地方政策
        is_national = any(kw in text for kw in national_keywords)
        
        # 查找地区
        found_province = None
        for p in provinces:
            if p in text:
                found_province = p
                break
        
        # 查找所有匹配的行业（支持多行业匹配）
        sorted_industries = sorted(industry_map.keys(), key=len, reverse=True)
        matched_industries = []
        matched_keywords = []
        
        for ind in sorted_industries:
            if ind in text:
                is_sub = False
                for existing in matched_keywords:
                    if ind in existing or existing in ind:
                        if len(ind) < len(existing):
                            is_sub = True
                            break
                if not is_sub:
                    matched_keywords = [k for k in matched_keywords if len(k) < len(ind) or ind not in k]
                    matched_keywords.append(ind)
                    matched_industries.append((ind, industry_map[ind]))
        
        # 综合板块处理：当提到综合板块但没提到具体子板块时，添加所有子板块
        subsector_configs = [
            ('金融', FINANCE_SUBSECTORS, FINANCE_EXCLUDE_KEYWORDS),
            ('新能源', NEW_ENERGY_SUBSECTORS, NEW_ENERGY_EXCLUDE_KEYWORDS),
            ('房地产', REAL_ESTATE_SUBSECTORS, REAL_ESTATE_EXCLUDE_KEYWORDS),
            ('医药', MEDICINE_SUBSECTORS, MEDICINE_EXCLUDE_KEYWORDS),
            ('自贸区', FTZ_SUBSECTORS, FTZ_EXCLUDE_KEYWORDS),
        ]
        
        for parent_name, subsectors, exclude_kw in subsector_configs:
            if parent_name in text and not any(kw in text for kw in exclude_kw):
                for sub_name, sub_code in subsectors:
                    matched_industries.append((sub_name, sub_code))
        
        # 特殊处理："新能源汽车" 等同于 "新能源车"
        if '新能源汽车' in text and '新能源车' not in matched_keywords:
            matched_keywords.append('新能源车')
            matched_industries.append(('新能源车', '881125'))
        
        # 国家政策：返回所有匹配行业的股票
        if is_national and matched_industries:
            all_stocks = []
            industry_results = []
            for ind_name, ind_code in matched_industries:
                result = self._get_industry_stocks(ind_name, ind_code)
                if result.get('matched'):
                    industry_results.append({
                        'name': ind_name,
                        'code': ind_code,
                        'count': len(result['stocks'])
                    })
                    all_stocks.extend(result['stocks'])
            
            # 去重
            seen_codes = set()
            unique_stocks = []
            for stock in all_stocks:
                if stock['代码'] not in seen_codes:
                    seen_codes.add(stock['代码'])
                    unique_stocks.append(stock)
            
            return {
                'matched': True,
                'policy': policy_text if isinstance(policy_text, str) else policy_text.get('标题', ''),
                'type': '国家政策',
                'industries': industry_results,
                'stocks': unique_stocks
            }
        
        # 地方政策：地区+行业双重筛选
        if found_province and matched_industries:
            all_stocks = []
            industry_results = []
            for ind_name, ind_code in matched_industries:
                result = self._get_province_industry_stocks(found_province, ind_name, ind_code)
                if result.get('matched'):
                    industry_results.append({
                        'name': ind_name,
                        'code': ind_code,
                        'count': len(result['stocks'])
                    })
                    all_stocks.extend(result['stocks'])
            
            seen_codes = set()
            unique_stocks = []
            for stock in all_stocks:
                if stock['代码'] not in seen_codes:
                    seen_codes.add(stock['代码'])
                    unique_stocks.append(stock)
            
            return {
                'matched': True,
                'policy': policy_text if isinstance(policy_text, str) else policy_text.get('标题', ''),
                'type': '地方政策',
                'region': found_province,
                'industries': industry_results,
                'stocks': unique_stocks
            }
        
        # 地方政策：只找到地区，没找到行业
        if found_province and not is_national:
            return self._get_province_stocks(found_province)
        
        # 国家政策：只找到行业，没找到明确的国家关键词
        if matched_industries:
            all_stocks = []
            industry_results = []
            for ind_name, ind_code in matched_industries:
                result = self._get_industry_stocks(ind_name, ind_code)
                if result.get('matched'):
                    industry_results.append({
                        'name': ind_name,
                        'code': ind_code,
                        'count': len(result['stocks'])
                    })
                    all_stocks.extend(result['stocks'])
            
            seen_codes = set()
            unique_stocks = []
            for stock in all_stocks:
                if stock['代码'] not in seen_codes:
                    seen_codes.add(stock['代码'])
                    unique_stocks.append(stock)
            
            return {
                'matched': True,
                'policy': policy_text if isinstance(policy_text, str) else policy_text.get('标题', ''),
                'type': '行业政策',
                'industries': industry_results,
                'stocks': unique_stocks
            }
        
        # 国家政策，返回全部沪深A股（剔除ST）
        if is_national:
            return self._get_all_a_stocks()
        
        # 如果都没匹配到，尝试智能匹配
        if found_province:
            return self._get_province_stocks(found_province)
        
        return {'matched': False, 'message': '未能识别具体行业或地区', 'stocks': []}
    
    def _get_industry_stocks(self, industry_name, industry_code):
        """获取同花顺行业板块成分股"""
        try:
            url = f'https://d.10jqka.com.cn/v2/blockrank/{industry_code}/199112/d10000.js'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://q.10jqka.com.cn/',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            text = response.text
            text = text[:-1]
            text = text.split('{"block":')[-1]
            text = '{"block":' + text
            # 替换 JavaScript null 为 Python None
            text = text.replace('null', 'None')
            data = eval(text)
            
            df = pd.DataFrame(data['block']['items'])
            
            # 使用固定列名映射（同花顺API返回的列名是固定的）
            col_mapping = {
                "5": "代码",
                "55": "名称", 
                "199112": "涨跌幅",
                "10": "价格",
                "13": "成交量"
            }
            
            # 只重命名存在的列
            existing_mapping = {k: v for k, v in col_mapping.items() if k in df.columns}
            df.rename(columns=existing_mapping, inplace=True)
            
            # 确保必要的列存在
            if '名称' not in df.columns or '代码' not in df.columns:
                print(f"警告: 缺少必要列，当前列名: {df.columns.tolist()}")
                return {'matched': False, 'message': '数据格式异常', 'stocks': []}
            
            # 剔除ST股票
            df = df[~df['名称'].str.contains('ST', na=False)]
            
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    '代码': row['代码'],
                    '名称': row['名称'],
                    '涨跌幅': row.get('涨跌幅', ''),
                    '价格': row.get('价格', ''),
                })
            
            return {
                'matched': True,
                'type': '行业',
                'name': industry_name,
                'stocks': stocks,
                'count': len(stocks)
            }
        except Exception as e:
            return {'matched': False, 'message': f'获取行业股票失败: {e}', 'stocks': []}
    
    def _get_province_industry_stocks(self, province, industry_name, industry_code):
        """获取地区+行业双重筛选的股票"""
        try:
            # 使用同花顺问财搜索获取地区+行业股票
            query = f'{province}注册地，{industry_name}概念'
            url = f'https://www.iwencai.com/unifiedwap/result?w={query}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.iwencai.com/',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            stock_list = []
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    code = cols[0].text.strip()
                    name = cols[1].text.strip()
                    
                    # 跳过ST股票
                    if 'ST' in name:
                        continue
                    
                    # 验证是6位数字代码
                    if re.match(r'\d{6}', code):
                        stock_list.append({
                            '代码': code,
                            '名称': name,
                        })
            
            if stock_list:
                return {
                    'matched': True,
                    'type': f'{province}{industry_name}',
                    'name': f'{province}_{industry_name}',
                    'stocks': stock_list,
                    'count': len(stock_list)
                }
            
            # 如果问财解析失败，尝试备用方法：先获取行业股票，再筛选地区
            return self._get_province_industry_stocks_fallback(province, industry_name, industry_code)
        except Exception as e:
            return self._get_province_industry_stocks_fallback(province, industry_name, industry_code)
    
    def _get_province_industry_stocks_fallback(self, province, industry_name, industry_code):
        """备用方法：获取行业股票后筛选地区"""
        try:
            # 先获取行业股票
            industry_result = self._get_industry_stocks(industry_name, industry_code)
            if not industry_result.get('matched'):
                return {'matched': False, 'message': '获取行业股票失败', 'stocks': []}
            
            industry_stocks = industry_result['stocks']
            if not industry_stocks:
                return {'matched': False, 'message': '行业股票为空', 'stocks': []}
            
            # 获取该地区所有股票（用于筛选）
            province_result = self._get_province_stocks(province)
            if not province_result.get('matched'):
                # 如果地区API失败，返回行业股票并提示
                return {
                    'matched': True,
                    'type': '行业',
                    'name': f'{industry_name}（{province}地区筛选暂不可用）',
                    'stocks': industry_stocks,
                    'count': len(industry_stocks),
                    'message': f'提示：无法精确筛选{province}地区股票，返回全国{industry_name}行业股票'
                }
            
            province_codes = set(s['代码'] for s in province_result['stocks'])
            
            # 筛选同时属于该地区的行业股票
            filtered_stocks = [s for s in industry_stocks if s['代码'] in province_codes]
            
            if not filtered_stocks:
                return {
                    'matched': True,
                    'type': '行业',
                    'name': f'{industry_name}（{province}地区无相关股票）',
                    'stocks': industry_stocks,
                    'count': len(industry_stocks),
                    'message': f'{province}地区暂无{industry_name}行业股票，返回全国{industry_name}行业股票'
                }
            
            return {
                'matched': True,
                'type': f'{province}{industry_name}',
                'name': f'{province}_{industry_name}',
                'stocks': filtered_stocks,
                'count': len(filtered_stocks)
            }
        except Exception as e:
            return {'matched': False, 'message': f'获取地区行业股票失败: {e}', 'stocks': []}
    
    def _get_province_stocks(self, province):
        """获取地区相关股票（注册地在该地区的A股）"""
        try:
            if province not in PROVINCE_MAP:
                return {'matched': False, 'message': f'不支持的地区: {province}', 'stocks': []}
            
            province_code = PROVINCE_MAP[province]
            
            # 使用同花顺API获取地区股票
            url = f'https://d.10jqka.com.cn/v2/blockrank/{province_code}/199112/d10000.js'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://q.10jqka.com.cn/',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            text = response.text
            text = text[:-1]
            text = text.split('{"block":')[-1]
            text = '{"block":' + text
            text = text.replace('null', 'None')
            data = eval(text)
            
            df = pd.DataFrame(data['block']['items'])
            
            col_mapping = {
                "5": "代码",
                "55": "名称", 
                "199112": "涨跌幅",
                "10": "价格",
                "13": "成交量"
            }
            
            existing_mapping = {k: v for k, v in col_mapping.items() if k in df.columns}
            df.rename(columns=existing_mapping, inplace=True)
            
            if '名称' not in df.columns or '代码' not in df.columns:
                return {'matched': False, 'message': '数据格式异常', 'stocks': []}
            
            # 剔除ST股票
            df = df[~df['名称'].str.contains('ST', na=False)]
            
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    '代码': row['代码'],
                    '名称': row['名称'],
                    '涨跌幅': row.get('涨跌幅', ''),
                    '价格': row.get('价格', ''),
                })
            
            return {
                'matched': True,
                'type': '地区',
                'name': province,
                'stocks': stocks,
                'count': len(stocks)
            }
        except Exception as e:
            return {'matched': False, 'message': f'获取地区股票失败: {e}', 'stocks': []}
    
    def _get_all_a_stocks(self):
        """获取全部沪深A股（剔除ST和科创板）"""
        try:
            # 使用新浪财经API获取全部A股列表
            all_stocks = []
            page = 1
            page_size = 100
            
            url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://finance.sina.com.cn/',
            }
            
            while True:
                params = {
                    'page': str(page),
                    'num': str(page_size),
                    'sort': 'symbol',
                    'asc': '1',
                    'node': 'hs_a',
                    'symbol': '',
                    '_s_r_a': 'page',
                }
                
                # 添加重试逻辑
                max_retries = 3
                response = None
                for retry in range(max_retries):
                    try:
                        response = requests.get(url, params=params, headers=headers, timeout=15)
                        if response.status_code == 200:
                            break
                        elif response.status_code == 502:
                            if retry < max_retries - 1:
                                time.sleep(2)
                                continue
                            else:
                                # 502错误，停止获取
                                break
                    except requests.exceptions.ConnectionError:
                        if retry < max_retries - 1:
                            time.sleep(2)
                            continue
                        raise
                
                if response is None or response.status_code != 200:
                    break
                
                data = json.loads(response.text)
                if not data:
                    break
                    
                all_stocks.extend(data)
                
                if len(data) < page_size:
                    break
                page += 1
                
                # 限制最多获取50页（5000只股票）
                if page > 50:
                    break
            
            # 转换为标准格式
            stocks = []
            for item in all_stocks:
                code = item.get('code', '')
                name = item.get('name', '')
                price = item.get('trade', '')
                
                # 只保留A股（60/00/30开头），排除科创板（688开头）和ST股票
                if code.startswith(('60', '00', '30')) and 'ST' not in name:
                    # 获取涨跌幅
                    change = item.get('pricechange', '')
                    stocks.append({
                        '代码': code,
                        '名称': name,
                        '价格': price,
                        '涨跌幅': change,
                    })
            
            return {
                'matched': True,
                'type': '国家政策',
                'name': '沪深A股全部',
                'stocks': stocks,
                'count': len(stocks)
            }
        except Exception as e:
            return {'matched': False, 'message': f'获取全部A股失败: {e}', 'stocks': []}
    
    def save_policy_stocks_excel(self, policy_info, date_str):
        """将政策利好对应股票保存到Excel"""
        if not policy_info.get('matched'):
            print(f"未匹配到相关股票: {policy_info.get('message', '')}")
            return
        
        stocks = policy_info['stocks']
        if not stocks:
            print("未找到相关股票")
            return
        
        df = pd.DataFrame(stocks)
        
        # 将价格列转换为数值类型
        df['价格'] = pd.to_numeric(df['价格'], errors='coerce')
        
        # 剔除价格<3和价格>50的股票
        df = df[(df['价格'] >= 3) & (df['价格'] <= 50)]
        
        # 剔除科创板股票（代码以688开头）
        df = df[~df['代码'].astype(str).str.startswith('688')]
        
        # 按价格从高到低排列
        df = df.sort_values(by='价格', ascending=False)
        
        # 生成文件名
        filename = f"政策利好股票_{policy_info['type']}_{policy_info['name']}_{date_str}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # 使用带重试的保存方法
        if save_excel_with_retry(df, filepath):
            print(f"已保存 {len(df)} 条{policy_info['type']}利好股票到 {filepath}（已剔除价格<3和价格>50的股票，按价格降序排列）")
    
    def fetch_headline_news(self, date_str=None):
        """从同花顺首页抓取头条新闻"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.10jqka.com.cn/',
            }
            
            # 从首页抓取头条新闻
            r = requests.get('https://www.10jqka.com.cn/', headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            all_headlines = []
            seen_titles = set()
            
            # 查找包含头条新闻的div
            for div in soup.find_all(['div', 'section']):
                classes = div.get('class', [])
                text = div.get_text()
                if '头条' in text and len(text) > 100:
                    # 查找新闻链接
                    for a in div.find_all('a', href=True):
                        href = a.get('href', '')
                        
                        # 只处理news.10jqka链接
                        if 'news.10jqka' not in href:
                            continue
                        
                        # 从h3或h4标签中提取标题
                        title_tag = a.find(['h3', 'h4'])
                        if title_tag:
                            title = title_tag.get_text().strip()
                        else:
                            title = a.get_text().strip()
                        
                        if title and title not in seen_titles and len(title) > 5:
                            seen_titles.add(title)
                            
                            # 从链接获取详情
                            detail_info = self._fetch_news_detail(href)
                            
                            all_headlines.append({
                                '标题': detail_info.get('标题', title),
                                '详情': detail_info.get('详情', ''),
                                '链接': href,
                                '时间': detail_info.get('时间', ''),
                                '来源': detail_info.get('来源', ''),
                            })
                            
                            print(f"已获取: {title[:50]}...")
                        
                        if len(all_headlines) >= 50:
                            break
                    
                    if len(all_headlines) >= 50:
                        break
            
            print(f"共获取到 {len(all_headlines)} 条头条新闻")
            return all_headlines
        except Exception as e:
            print(f"获取头条新闻失败: {e}")
            return []
    
    def _fetch_news_detail(self, url):
        """从新闻链接获取详情、时间和来源"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.10jqka.com.cn/',
            }
            
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 获取标题
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            # 获取时间
            time_str = ''
            time_tag = soup.find('span', class_=lambda x: x and 'time' in x.lower())
            if not time_tag:
                time_tag = soup.find('span', string=lambda x: x and re.match(r'\d{4}-\d{2}-\d{2}', x))
            if time_tag:
                time_str = time_tag.get_text().strip()
            
            # 获取来源
            source_str = ''
            source_tag = soup.find('span', class_=lambda x: x and 'source' in x.lower())
            if not source_tag:
                source_tag = soup.find('a', class_=lambda x: x and 'source' in x.lower())
            if source_tag:
                source_str = source_tag.get_text().strip()
            
            # 获取详情内容
            content_tag = soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'article' in x.lower() or 'detail' in x.lower()))
            if not content_tag:
                content_tag = soup.find('div', id=lambda x: x and ('content' in x.lower() or 'article' in x.lower()))
            
            detail = ''
            if content_tag:
                # 获取所有段落文本
                paragraphs = content_tag.find_all('p')
                detail = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return {
                '标题': title,
                '详情': detail,
                '时间': time_str,
                '来源': source_str,
            }
        except Exception as e:
            print(f"获取新闻详情失败 {url}: {e}")
            return {'标题': '', '详情': '', '时间': '', '来源': ''}
    
    def save_headline_news(self, date_str=None):
        """保存头条新闻到独立的Excel文件"""
        try:
            if date_str is None:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            headlines = self.fetch_headline_news(date_str)
            if not headlines:
                print("未获取到头条新闻")
                return False
            
            df_headlines = pd.DataFrame(headlines)
            
            # 头条新闻保存到独立文件
            filepath = os.path.join(self.output_dir, f'news头条_{date_str}.xlsx')
            
            # 使用字典指定sheet名称
            if save_excel_with_retry({'头条': df_headlines}, filepath):
                print(f"已保存 {len(headlines)} 条头条新闻到 {filepath} (头条sheet)")
                return True
            return False
        except Exception as e:
            print(f"保存头条新闻失败: {e}")
            return False
    
    def save_stock_codes_to_file(self):
        """保存股票代码到gp_codes.py文件"""
        try:
            result = self._get_all_a_stocks()
            if not result.get('matched'):
                print(f"获取股票数据失败: {result.get('message', '')}")
                return False
            
            stocks = result['stocks']
            update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 生成格式化的Python文件内容
            lines = [
                '# 股票数据文件',
                '# 自动生成，请勿手动修改',
                f'# 更新时间: {update_time}',
                f'# 股票数量: {len(stocks)}',
                '',
                'STOCKS_DATA = [',
            ]
            
            # 格式化每个股票数据
            for stock in stocks:
                code = stock['代码']
                name = stock['名称']
                price = stock['价格']
                change = stock['涨跌幅']
                lines.append(f"    {{'代码': '{code}', '名称': '{name}', '价格': '{price}', '涨跌幅': {change}}},")
            
            lines.append(']')
            lines.append('')
            
            content = '\n'.join(lines)
            
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gp_codes.py')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"已保存 {len(stocks)} 只股票数据到 gp_codes.py")
            return True
        except Exception as e:
            print(f"保存股票数据失败: {e}")
            return False
    
    def start_scheduler(self):
        """启动定时任务"""
        print("启动7*24快讯抓取程序...")
        print("每5分钟抓取一次数据")
        print(f"数据保存目录: {self.output_dir}")
        
        # 立即执行一次
        self.run_fetch()
        self.save_headline_news()
        
        # 设置定时任务
        schedule.every(5).minutes.do(self.run_fetch)
        schedule.every(5).minutes.do(self.save_headline_news)
        
        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    scraper = NewsScraper()
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 3 and sys.argv[1] == '--analyze':
            # 新闻分析模式：根据标题和内容分析利好行业/板块
            title = sys.argv[2]
            content = sys.argv[3]
            date_str = datetime.now().strftime('%Y-%m-%d')
            print(f"新闻分析模式: {title}")
            result = scraper.analyze_news_stocks(title, content)
            if result.get('matched'):
                scraper.save_policy_stocks_excel(result, date_str)
                print(f"识别到的行业/板块: {', '.join([ind['name'] for ind in result['industries']])}")
            else:
                print(f"分析失败: {result.get('message', '未知错误')}")
        elif len(sys.argv) > 2 and sys.argv[1] == '--policy':
            # 政策利好股票分析模式
            policy_text = sys.argv[2]
            date_str = datetime.now().strftime('%Y-%m-%d')
            print(f"政策利好股票分析模式: {policy_text}")
            result = scraper.analyze_policy_stocks(policy_text)
            if result.get('matched'):
                scraper.save_policy_stocks_excel(result, date_str)
            else:
                print(f"分析失败: {result.get('message', '未知错误')}")
        elif len(sys.argv) > 1:
            # 指定日期模式
            date_str = sys.argv[1]
            print(f"指定日期模式: {date_str}")
            scraper.fetch_and_save_specific_date(date_str)
        else:
            # 默认模式：获取当天数据并定时抓取
            scraper.start_scheduler()
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"程序运行出错: {e}")
