import requests
import json
import pandas as pd
from datetime import datetime
import os
import time
import akshare as ak
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.qq.com/',
}

# 获取股票代码列表
def get_stock_codes():
    """从新浪API获取股票代码列表"""
    print('获取股票代码列表...')
    all_codes = {'sh': [], 'sz': []}
    
    # 获取沪市A股
    page = 1
    while True:
        url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num=80&sort=price&asc=0&node=sh_a&symbol=&_s_r_a=auto'
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = json.loads(resp.text)
            if not data:
                break
            for item in data:
                code = item.get('code', '')
                if code.startswith(('600', '601', '603', '605', '688')):
                    all_codes['sh'].append(code)
            if len(data) < 80:
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f'  沪市第{page}页请求失败: {e}')
            break
    
    # 获取深市A股
    page = 1
    while True:
        url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num=80&sort=price&asc=0&node=sz_a&symbol=&_s_r_a=auto'
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = json.loads(resp.text)
            if not data:
                break
            for item in data:
                code = item.get('code', '')
                if code.startswith(('000', '001', '002', '003', '300', '301')):
                    all_codes['sz'].append(code)
            if len(data) < 80:
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f'  深市第{page}页请求失败: {e}')
            break
    
    print(f'  沪市: {len(all_codes["sh"])}只, 深市: {len(all_codes["sz"])}只')
    return all_codes

# 获取腾讯行情数据
def get_tencent_quotes(codes):
    """从腾讯API获取行情数据"""
    all_stocks = []
    batch_size = 60
    
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        code_str = ','.join(batch)
        url = f'https://qt.gtimg.cn/q={code_str}'
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            lines = resp.text.strip().split('\n')
            
            for line in lines:
                if '~' not in line:
                    continue
                
                parts = line.split('~')
                if len(parts) < 50:
                    continue
                
                name = parts[1]
                if 'ST' in name:
                    continue
                
                stock_info = {
                    '代码': parts[2],
                    '名称': name,
                    '价格': float(parts[3] or 0),
                    '涨跌幅': float(parts[32] or 0),
                    '涨跌': float(parts[31] or 0),
                    '成交额': float(parts[37] or 0) * 10000,
                    '成交量': float(parts[36] or 0),
                    '总市值': float(parts[44] or 0) * 100000000,
                    '流通市值': float(parts[45] or 0) * 100000000,
                    '市盈率(动)': float(parts[39] or 0),
                    '市净率': float(parts[46] or 0),
                    '换手率': float(parts[38] or 0),
                }
                all_stocks.append(stock_info)
            
            print(f'  已获取第{i//batch_size + 1}批')
            time.sleep(0.3)
            
        except Exception as e:
            print(f'  第{i//batch_size + 1}批请求失败: {e}')
    
    return all_stocks

# 获取单只股票财务数据
def get_single_financial(code):
    """获取单只股票的财务数据"""
    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
        if not df.empty:
            latest = df.iloc[0]
            return code, {
                '每股收益': str(latest.get('基本每股收益', '')),
                '每股净资产': str(latest.get('每股净资产', '')),
                '净资产收益率': str(latest.get('净资产收益率', '')),
                '毛利率': str(latest.get('销售毛利率', '')),
                '净利润增长率': str(latest.get('净利润同比增长率', '')),
                '营收增长率': str(latest.get('营业总收入同比增长率', '')),
            }
    except:
        pass
    return code, None

# 获取财务数据（多线程）
def get_financial_data(all_codes):
    """从同花顺获取财务数据（多线程）"""
    print('获取财务数据...')
    financial_dict = {}
    
    # 合并所有代码
    codes = []
    for market in all_codes.values():
        codes.extend(market)
    
    # 过滤需要的代码
    target_codes = [c for c in codes if c.startswith(('600', '601', '603', '605', '000', '001', '002', '003', '300', '301'))]
    
    total = len(target_codes)
    print(f'  共 {total} 只股票需要获取财务数据')
    
    # 使用多线程获取
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_single_financial, code): code for code in target_codes}
        
        completed = 0
        for future in as_completed(futures):
            code, data = future.result()
            if data:
                financial_dict[code] = data
            
            completed += 1
            if completed % 200 == 0:
                print(f'  已获取 {completed}/{total} 只股票财务数据')
            time.sleep(0.05)
    
    print(f'  共获取 {len(financial_dict)} 只股票财务数据')
    return financial_dict

# 主程序
print('='*60)
print('开始获取股票数据...')
print('='*60)

# 获取股票代码
stock_codes = get_stock_codes()

# 获取沪市主板数据
print('\n获取沪市主板（600/601/603/605）行情数据...')
sh_codes = [f'sh{c}' for c in stock_codes['sh'] if c.startswith(('600', '601', '603', '605'))]
sh_stocks = get_tencent_quotes(sh_codes)
print(f'沪市主板: {len(sh_stocks)} 只')

# 获取深市主板数据
print('\n获取深市主板（000/001/002/003）行情数据...')
sz_codes = [f'sz{c}' for c in stock_codes['sz'] if c.startswith(('000', '001', '002', '003'))]
sz_stocks = get_tencent_quotes(sz_codes)
print(f'深市主板: {len(sz_stocks)} 只')

# 获取创业板数据
print('\n获取创业板（300/301）行情数据...')
cyb_codes = [f'sz{c}' for c in stock_codes['sz'] if c.startswith(('300', '301'))]
cyb_stocks = get_tencent_quotes(cyb_codes)
print(f'创业板: {len(cyb_stocks)} 只')

# 创建DataFrame
df_sh = pd.DataFrame(sh_stocks)
df_sz = pd.DataFrame(sz_stocks)
df_cyb = pd.DataFrame(cyb_stocks)

# 获取财务数据
financial_dict = get_financial_data(stock_codes)

# 添加财务数据字段
for df in [df_sh, df_sz, df_cyb]:
    df['每股收益'] = ''
    df['每股净资产'] = ''
    df['净资产收益率'] = ''
    df['毛利率'] = ''
    df['净利润增长率'] = ''
    df['营收增长率'] = ''
    
    # 填充财务数据
    if financial_dict:
        for i, code in enumerate(df['代码']):
            if code in financial_dict:
                fin_data = financial_dict[code]
                for key, value in fin_data.items():
                    df.loc[df['代码'] == code, key] = value

# 按价格降序排列
if not df_sh.empty:
    df_sh = df_sh.sort_values('价格', ascending=False).reset_index(drop=True)
if not df_sz.empty:
    df_sz = df_sz.sort_values('价格', ascending=False).reset_index(drop=True)
if not df_cyb.empty:
    df_cyb = df_cyb.sort_values('价格', ascending=False).reset_index(drop=True)

# 打印统计信息
print('\n各板块股票数量:')
print(f'  沪市主板: {len(df_sh)} 只')
print(f'  深市主板: {len(df_sz)} 只')
print(f'  创业板: {len(df_cyb)} 只')

# 创建Excel文件
date_str = datetime.now().strftime('%Y-%m-%d')
output_dir = 'news_data'
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, f'基本面数据_{date_str}.xlsx')

# 保存到Excel
with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
    if not df_sh.empty:
        df_sh.to_excel(writer, sheet_name='沪市主板', index=False)
    if not df_sz.empty:
        df_sz.to_excel(writer, sheet_name='深市主板', index=False)
    if not df_cyb.empty:
        df_cyb.to_excel(writer, sheet_name='创业板', index=False)

print(f'\n已保存到: {filepath}')
print(f'包含 3 个sheet: 沪市主板, 深市主板, 创业板')
print('\n数据字段: 代码、名称、价格、涨跌幅、涨跌、成交额、成交量、总市值、流通市值、市盈率(动)、市净率、换手率、每股收益、每股净资产、净资产收益率、毛利率、净利润增长率、营收增长率')
