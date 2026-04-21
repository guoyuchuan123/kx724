import requests
import json
import pandas as pd
from datetime import datetime
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://q.10jqka.com.cn/',
    'Content-Type': 'application/json',
}

# 小金属概念股票列表
code_list = [
    {"market": "17", "codes": ["600111", "600259", "600281", "600301", "600392", "600456", "600459", "600549", "601958", "688750"]},
    {"market": "33", "codes": ["300328", "301026", "000831", "000426", "000960", "000962", "001280", "002149", "002167", "002182", "002428", "002738", "002978", "000657", "002378", "002842", "000688", "001257"]},
    {"market": "151", "codes": ["920068"]}
]

url = 'https://quota-h.10jqka.com.cn/fuyao/common_hq_aggr/quote/v1/multi_last_snapshot'

payload = {
    "code_list": code_list,
    "trade_class": "intraday",
    "data_fields": ["55", "10", "199112", "264648", "19", "6"],
    "lang": "zh_cn",
    "gpid": 1
}

print('获取小金属概念板块数据...')
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    data = resp.json()
    
    # 解析数据
    stock_list = []
    quote_data = data.get('data', {}).get('quote_data', [])
    
    for item in quote_data:
        values = item.get('value', [])
        if not values:
            continue
        v = values[0]
        stock_list.append({
            '代码': item.get('code', ''),
            '名称': v[0],
            '价格': float(v[5]) if len(v) > 5 else 0,
            '涨跌幅': float(v[4]) if len(v) > 4 else 0,
            '涨跌': float(v[3]) if len(v) > 3 else 0,
        })
    
    # 创建DataFrame
    df = pd.DataFrame(stock_list)
    
    # 剔除ST股票
    df = df[~df['名称'].str.contains('ST', na=False)]
    
    # 剔除科创板股票（688开头）和北交所股票（920开头）
    df = df[~df['代码'].str.startswith(('688', '920'))]
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # 打印数据
    print('\n小金属概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'小金属_{date_str}.xlsx')
    
    # 保存到Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='小金属', index=False)
    
    print(f'\n已保存到: {filepath}')
    print(f'共 {len(df)} 只股票')
    
except Exception as e:
    print(f'获取数据失败: {e}')
    import traceback
    traceback.print_exc()
