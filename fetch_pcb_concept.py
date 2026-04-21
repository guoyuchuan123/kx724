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

url = 'https://quota-h.10jqka.com.cn/fuyao/common_hq_aggr/quote/v1/multi_last_snapshot'

# PCB概念股票列表（用户提供）
pcb_names = [
    '凯华材料', '帝尔激光', '斯迪克', '泰金新能', '则成电子', '凯格精机', '凯盛科技', '天通股份', '快克智能', '广合科技',
    '传艺科技', '博杰股份', '共进股份', '合力泰', '欧科亿', '瑞丰高材', '东山精密', '中钨高新', '东材科技', '胜宏科技',
    '雅葆轩', '光莆股份', '锐科激光', '光洋股份', '万源通', '威贸电子', '德龙激光', '迅捷兴', '力源信息', '荣亿精密',
    '海目星', '东威科技', '圣泉集团', '昊志机电', '澳弘电子', '方邦股份', '康达新材', '兆驰股份', '德福科技', '兴森科技',
    '埃科光电', '生益电子', '深南电路', '科强股份', '华正新材', '路维光电', '明阳电路', '乔锋智能', '景旺电子', '温州宏丰',
    '美联新材', '一博科技', '波长光电', '先导智能', '金百泽', '英诺激光', '三孚新科', '燕麦科技', '本川智能', '强力新材',
    '鼎泰高科', '华工科技', '宏和科技', '银禧科技', '沪电股份', '天承科技', '大族数控', '铜冠铜箔', '立方控股', '木林森',
    '思泰克', '世名科技', '菲利华', '新锐股份', '赛腾股份', '天准科技', '楚江新材', '赛意信息', '中京电子', '平安电工',
    '生益科技', '泰永长征', '强达电路', '四会富仕', '怡合达', '德邦科技', '贤丰控股', '方正科技', '博敏电子', '金禄电子',
    '惠柏新材', '天津普林', '云汉芯城', '容大感光', '利和兴', '有研粉材', '正业科技', '晨丰科技', '鹏鼎控股', '嘉元科技',
    '铜陵有色', '芯碁微装', '同益股份', '劲拓股份', '奥士康', '合锻智能', '光华科技', '依顿电子', '中国巨石', '金太阳',
    '矩子科技', '艾森股份', '协和电子', '广信材料', '新广益', '瑞华泰', '沃特股份', '大族激光', '金信诺', '崇达技术',
    '四创电子', '中材科技', '骏亚科技', '华测检测', '永杰新材', '四川九洲', '杭华股份', '超颖电子', '泰和科技', '骏成科技',
    '天山电子', '北方铜业', '杰普特', '普天科技', '科翔股份', '万朗磁塑', '瑞德智能', '金安国纪', '世运电路', '中富电路',
    '中一科技', '宏昌电子', '扬帆新材', '智信精密', '瀚川智能', '久日新材', '肯特股份', '莱特光电', '东方材料', '中英科技',
    '日联科技', '长海股份', '威尔高', '亿道信息', '西陇科学', '捷佳伟创', '同宇新材', '国光电器', '壹石通', '亨通股份',
    '松井股份', '龙旗科技', '电连技术', '航天智造', '佰奥智能', '冠捷科技', '超声电子', '江南新材', '弘信电子', '诺德股份',
    '中科电气', '宏英智能', '满坤科技', '顺络电子', '信通电子', '昊华科技', '雪祺电气', '光韵达', '逸豪新材', '富佳股份',
    '英可瑞', '新北洋', '豪江智能', '维科精密', '奕东电子', '大为股份', '山东玻纤', '宝鼎科技', '红板科技', '福斯特',
    '国际复材', '民爆光电', '深康佳Ａ', '强瑞技术', '南亚新材', '长园'
]

# 从gp_codes.py获取股票代码
print('获取PCB概念股票代码...')

# 读取gp_codes.py获取代码映射
import re
with open('d:/kx724/gp_codes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取股票代码映射
code_map = {}
pattern = r"\{'代码':\s*'(\d+)',\s*'名称':\s*'([^']+)'"
for match in re.finditer(pattern, content):
    code_map[match.group(2)] = match.group(1)

# 获取PCB股票代码
sh_codes = []
sz_codes = []
bj_codes = []

for name in pcb_names:
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
print('获取PCB概念板块数据...')
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
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # PCB设备分类（用户提供）
    pcb_equipment = [
        '凯格精机', '博杰股份', '德龙激光', '东威科技', '英诺激光', 
        '燕麦科技', '鼎泰高科', '大族数控', '思泰克', '天准科技', 
        '正业科技', '芯碁微装', '劲拓股份', '日联科技'
    ]
    
    # 树脂分类（用户提供）
    resin = [
        '东材科技', '圣泉集团', '康达新材', '世名科技', '宏昌电子', 
        '同宇新材'
    ]
    
    # 服务器PCB分类（用户提供）
    server_pcb = [
        '广合科技', '东山精密', '生益电子', '深南电路', '景旺电子', 
        '沪电股份', '中京电子', '博敏电子', '金信诺', '崇达技术', 
        '世运电路', '超声电子'
    ]
    
    # 通讯PCB分类（用户提供）
    communication_pcb = [
        '广合科技', '兴森科技', '生益电子', '深南电路', '景旺电子', 
        '金百泽', '本川智能', '沪电股份', '金禄电子', '鹏鼎控股', 
        '金信诺', '骏亚科技', '普天科技', '科翔股份', '中富电路'
    ]
    
    # PCB化学品分类（用户提供）
    pcb_chemicals = [
        '天承科技', '斯迪克', '松井股份', '容大感光', '泰和科技', 
        '光华科技', '东方材料', '杭华股份', '西陇科学'
    ]
    
    # PCB铜箔分类（用户提供）
    pc_copper_foil = [
        '中一科技', '德福科技', '嘉元科技', '铜冠铜箔', '逸豪新材', 
        '宝鼎科技', '温州宏丰', '亨通股份'
    ]
    
    # 电子布分类（用户提供）
    electronic_cloth = [
        '菲利华', '宏和科技', '中材科技', '金安国纪', '中国巨石', 
        '国际复材', '宏昌电子'
    ]
    
    # 创建分类字典
    category_stocks = {
        '全部': df,
        'PCB设备': df[df['名称'].isin(pcb_equipment)],
        '树脂': df[df['名称'].isin(resin)],
        '服务器PCB': df[df['名称'].isin(server_pcb)],
        '通讯PCB': df[df['名称'].isin(communication_pcb)],
        'PCB化学品': df[df['名称'].isin(pcb_chemicals)],
        'PCB铜箔': df[df['名称'].isin(pc_copper_foil)],
        '电子布': df[df['名称'].isin(electronic_cloth)],
    }
    
    # 打印分类统计
    print('\n分类统计:')
    for category, stocks_df in category_stocks.items():
        print(f'  {category}: {len(stocks_df)} 只')
    
    # 打印全部数据
    print('\nPCB概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'PCB概念_{date_str}.xlsx')
    
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
