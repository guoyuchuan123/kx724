import requests
import json
import pandas as pd
from datetime import datetime
import os
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://q.10jqka.com.cn/',
    'Content-Type': 'application/json',
}

url = 'https://quota-h.10jqka.com.cn/fuyao/common_hq_aggr/quote/v1/multi_last_snapshot'

# 算力租赁概念股票列表
compute_rental_names = [
    '品高股份', '艾布鲁', '利通电子', '华升股份', '福鞍股份', '康盛股份', '合力泰',
    '并行科技', '中嘉博创', '凯添燃气', '超讯通信', '*ST金刚', '晶科科技', '广脉科技',
    '扬电科技', '奥瑞德', '汉鑫科技', '工业富联', '金开新能', 'ST智知', '神州数码',
    '三人行', '海兰信', 'ST福能', '中青宝', '凤凰传媒', '*ST宇顺', '爱施德',
    '云天励飞-U', '中科曙光', '中国能建', '海南华铁', '江苏有线', '中贝通信',
    '软通动力', '优刻得-W', '启明信息', '中国联通', '真视通', '行云科技', '宜通世纪',
    '同方股份', '佳力图', '协鑫能科', '国联股份', '锦龙股份', '广电运通', '吉视传媒',
    '科大讯飞', '恒润股份', '东方材料', '宇信科技', '众合科技', '华策影视', '浦东建设',
    '亚康股份', '安诺其', '天和防务', '*ST正平', '艾可蓝', '国网信通', '浪潮信息',
    '深信服', '常山北明', '蕾奥规划', 'ST迪威迅', '中国移动', '中科金财', '迈信林',
    '东华软件', '梦网科技', '华孚时尚', '贵广网络', '彩讯股份', '南威软件', '阿尔特',
    '万马科技', '宁夏建材', '航锦科技', '弘信电子', '纵横通信', '人民网', '朗科科技',
    '恒为科技', '中富通', '神州泰岳', '协创数据', '天娱数科', '世纪华通', '宝兰德',
    '设计总院', '城地香江', '奥雅股份', '佳华科技', '*ST新元', '信通电子', '新开普',
    '汇纳科技', '旋极信息', '科华数据', '万达信息', '鸿博股份', '华数传媒', 'ST中装',
    '海南高速', '网宿科技', '嘉环科技', '中创环保', '首都在线', '中辰股份', '飞利信',
    '东阳光', '紫光股份', '云从科技-UW', '东方国信', '湖北广电', '天亿马', '银信科技',
    '浙大网新', '农尚环境', '天威视讯', '平治信息', '智微智能', '创业黑马', '浙数文化',
    '青云科技-U', '润泽科技', '兴民智通', '汇金股份', 'ST景谷', '新致软件', '浙文互联',
    '南凌科技', '思特奇', '南兴股份', '广电网络', '日科化学', '杭钢股份', '立昂技术',
    '特发信息', '垒知集团', '南网数字', '云赛智联', '宝信软件', 'ST恒信', '铜牛信息',
    '长信科技', '宏景科技', '甘咨询', '顺网科技', '大位科技', '电光科技', '深桑达Ａ',
    '慧辰股份', '证通电子', '美利云', '数据港', '莲花控股', '光环新网', '大名城',
    '元道通信', '京源环保', '奥飞数据', '直真科技', '杰创智能', '有方科技', '群兴玩具',
    '*ST东易', '润建股份', '亿田智能', '实达集团', '锦鸡股份'
]

# 从gp_codes.py获取股票代码
print('获取算力租赁概念股票代码...')

# 读取gp_codes.py获取代码映射
with open('d:/kx724/gp_codes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取股票代码映射
code_map = {}
pattern = r"\{'代码':\s*'(\d+)',\s*'名称':\s*'([^']+)'"
for match in re.finditer(pattern, content):
    code_map[match.group(2)] = match.group(1)

# 获取算力租赁股票代码
sh_codes = []
sz_codes = []
bj_codes = []

for name in compute_rental_names:
    if name in code_map:
        code = code_map[name]
        if code.startswith('6'):
            sh_codes.append(code)
        elif code.startswith('0') or code.startswith('3'):
            sz_codes.append(code)
        elif code.startswith('8') or code.startswith('4') or code.startswith('9'):
            bj_codes.append(code)
    else:
        print(f'未找到股票代码: {name}')

code_list = []
if sh_codes:
    code_list.append({"market": "17", "codes": sh_codes})
if sz_codes:
    code_list.append({"market": "33", "codes": sz_codes})
if bj_codes:
    code_list.append({"market": "151", "codes": bj_codes})

payload = {
    "code_list": code_list,
    "trade_class": "intraday",
    "data_fields": ["55", "10", "199112", "264648", "19", "6"],
    "lang": "zh_cn",
    "gpid": 1
}

print(f'共获取到 {len(sh_codes) + len(sz_codes) + len(bj_codes)} 只股票代码')
print('获取算力租赁概念板块数据...')
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
        price = v[5] if len(v) > 5 and v[5] is not None else 0
        change_pct = v[4] if len(v) > 4 and v[4] is not None else 0
        change = v[3] if len(v) > 3 and v[3] is not None else 0
        stock_list.append({
            '代码': item.get('code', ''),
            '名称': v[0],
            '价格': float(price),
            '涨跌幅': float(change_pct),
            '涨跌': float(change),
        })
    
    # 创建DataFrame
    df = pd.DataFrame(stock_list)
    
    # 剔除ST股票
    df = df[~df['名称'].str.contains('ST', na=False)]
    
    # 剔除科创板股票（688开头）和北交所股票（920开头）
    df = df[~df['代码'].str.startswith(('688', '920'))]
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # 算力调动平台分类
    compute_dispatch = [
        '品高股份', '并行科技', '中科曙光', '中贝通信', '软通动力', '广电运通',
        '东方材料', '朗科科技', '神州泰岳', '网宿科技', '首都在线', '紫光股份',
        '浙大网新', '青云科技-U', '思特奇', '顺网科技', '慧辰股份', '证通电子',
        '光环新网', '直真科技', '润建股份'
    ]
    
    # OpenClaw算力分类
    openclaw_compute = [
        '软通动力', '优刻得-W', '航锦科技', '网宿科技', '首都在线', '青云科技-U', '顺网科技', '莲花控股'
    ]
    
    # IDC分类
    idc = [
        '世纪华通', '科华数据', '东方国信', '浙大网新', '南兴股份', '杭钢股份',
        '立昂技术', '云赛智联', '证通电子', '美利云', '数据港', '光环新网', '奥飞数据'
    ]
    
    # 创建分类字典
    category_stocks = {
        '全部': df,
        '算力调动平台': df[df['名称'].isin(compute_dispatch)],
        'OpenClaw算力': df[df['名称'].isin(openclaw_compute)],
        'IDC': df[df['名称'].isin(idc)],
    }
    
    # 打印分类统计
    print('\n分类统计:')
    for category, stocks_df in category_stocks.items():
        print(f'  {category}: {len(stocks_df)} 只')
    
    # 打印全部数据
    print('\n算力租赁概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'算力租赁_{date_str}.xlsx')
    
    # 保存到Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, sheet_df in category_stocks.items():
            if len(sheet_df) > 0:
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'\n已保存到: {filepath}')
    print(f'包含 {len(category_stocks)} 个sheet: {list(category_stocks.keys())}')
    
except Exception as e:
    print(f'获取数据失败: {e}')
    import traceback
    traceback.print_exc()
