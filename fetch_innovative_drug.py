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

# 创新药概念股票列表
innovative_drug_names = [
    '昂利康', '多瑞医药', '科拓生物', 'ST香雪', '圣泉集团', '峆一药业', '赛伦生物', '华海药业',
    '通化金马', '德源药业', 'ST百灵', '锦波生物', '星昊医药', 'ST景峰', '新赣江', '瑞联新材',
    '嘉应制药', '君实生物-U', 'ST未名', '翰宇药业', '苑东生物', '梓橦宫', '尖峰集团', '百洋医药',
    '海翔药业', '莱美药业', '海欣股份', '三元基因', '朗坤科技', '万邦德', '回盛生物', '华测检测',
    '仙琚制药', '万泰生物', '欧林生物', '先达股份', '新开源', '华兰股份', '海辰药业', '汇宇制药-W',
    '华熙生物', '上海谊众', '广誉远', '重药控股', '上海凯宝', '金城医药', '华兰生物', '泰恩康',
    'ST诺泰', '辽宁成大', '贝泰妮', '云南白药', '百诚医药', '广生堂', '海南海药', '奇正藏药',
    '白云山', '特宝生物', '富祥药业', '上海莱士', '康缘药业', '同仁堂', '羚锐制药', '济民健康',
    '键凯科技', '长春高新', '华特达因', '西藏药业', '康辰药业', '上海医药', '安科生物', '联化科技',
    '兴齐眼药', '健民集团', '小方制药', '皓元医药', '柳药集团', '三生国健', 'ST人福', '万泽股份',
    '吉林敖东', '昆药集团', '八亿时空', '新华制药', '福瑞达', '步长制药', '凯因科技', '禾元生物-U',
    '国药现代', '南京新百', '华润三九', '万邦医药', '天士力', '片仔癀', '中源协和', '康泰生物',
    '立方制药', '甘李药业', '我武生物', '塞力医疗', '亚泰集团', '三力制药', '一品红', '恩威医药',
    '葵花药业', '药石科技', 'ST葫芦娃', '仟源医药', '赛升药业', '马应龙', '之江生物', '健康元',
    '济川药业', '宣泰医药', '智飞生物', '申联生物', '维康药业', '圣诺生物', '海思科', '威尔药业',
    '中旗股份', '博瑞医药', '九州通', '太龙药业', '丽珠集团', '仁和药业', '普洛药业', '鲁抗医药',
    '粤万年青', '诺诚健华', '华北制药', '东诚药业', '福安药业', '新天地', '奥翔药业', '桂林三金',
    '华丽家族', '透景生命', '神州细胞', '金石亚药', '昊帆生物', '华润双鹤', '乐普医疗', '泰格医药',
    '德展健康', '中国医药', '艾力斯', '华纳药厂', '何氏眼科', '九典制药', '圣湘生物', '浙江震元',
    '百奥泰', '北大医药', '佰仁医疗', '首药控股-U', '普蕊斯', '华人健康', '盘龙药业', '迦南科技',
    '千红制药', '成都先导', '科伦药业', '奥锐特', '太极集团', '达嘉维康', '亚太药业', '冠昊生物',
    '众生药业', '西点药业', '恒瑞医药', '百花医药', '复旦张江', '*ST赛隆', '热景生物', '辰欣药业',
    '海普瑞', '珍宝岛', '复星医药', '荣昌生物', '亚宝药业', '垒知集团', '罗欣药业', '华森制药',
    '九洲药业', '佐力药业', '汉商集团', '健友股份', '陇神戎发', '沃森生物', '东北制药', '千金药业',
    '贝达药业', '华邦健康', '奥赛康', '金花股份', '博济医药', '微芯生物', '亚虹医药-U', '九芝堂',
    '泓博医药', '科兴制药', '华东医药', '康弘药业', '海创药业-U', '力生制药', '艾德生物', '益方生物-U',
    '通化东宝', '海正药业', '诺思格', '凯莱英', '恩华药业', '必贝特-U', '南新制药', '常山药业',
    '新天药业', '泽璟制药-U', '盟科药业-U', '诚达药业', '北陆药业', '振东制药', '润都股份', '中恒集团',
    '艾迪药业', '以岭药业', '红日药业', '吉贝尔', '亿帆医药', '浙江医药', '睿智医药', '海特生物',
    '康龙化成', '吉华集团', '信立泰', '汉森制药', '凯普生物', '哈三联', '精华制药', '迪哲医药-U',
    '博腾股份', '新诺威', '中 关 村', '福元医药', '迈威生物-U', '海王生物', '悦康药业', '智翔金泰-U',
    '华神科技', '美迪西', '方盛制药', '津药药业', '舒泰神', '京新药业', '益佰制药', '誉衡药业',
    '康芝药业', '双鹭药业', '百济神州', '金陵药业', '昭衍新药', '阳光诺和', '前沿生物-U', '益诺思',
    '百利天恒', '灵康药业', '联环药业', '哈药股份', '康恩贝', '瑞康医药', '药明康德', '诺思兰德'
]

# 从gp_codes.py获取股票代码
print('获取创新药概念股票代码...')

# 读取gp_codes.py获取代码映射
with open('d:/kx724/gp_codes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取股票代码映射
code_map = {}
pattern = r"\{'代码':\s*'(\d+)',\s*'名称':\s*'([^']+)'"
for match in re.finditer(pattern, content):
    code_map[match.group(2)] = match.group(1)

# 获取创新药股票代码
sh_codes = []
sz_codes = []
bj_codes = []

for name in innovative_drug_names:
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
print('获取创新药概念板块数据...')

# 分批请求数据（每批最多50只股票）
def batch_request(all_codes, batch_size=50):
    stock_list = []
    for i in range(0, len(all_codes), batch_size):
        batch = all_codes[i:i+batch_size]
        batch_code_list = []
        sh_batch = [c for c in batch if c.startswith('6')]
        sz_batch = [c for c in batch if c.startswith(('0', '3'))]
        bj_batch = [c for c in batch if c.startswith(('8', '4', '9'))]
        if sh_batch:
            batch_code_list.append({"market": "17", "codes": sh_batch})
        if sz_batch:
            batch_code_list.append({"market": "33", "codes": sz_batch})
        if bj_batch:
            batch_code_list.append({"market": "151", "codes": bj_batch})
        
        batch_payload = {
            "code_list": batch_code_list,
            "trade_class": "intraday",
            "data_fields": ["55", "10", "199112", "264648", "19", "6"],
            "lang": "zh_cn",
            "gpid": 1
        }
        
        try:
            resp = requests.post(url, headers=headers, json=batch_payload, timeout=10)
            data = resp.json()
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
        except Exception as e:
            print(f'批次 {i//batch_size + 1} 请求失败: {e}')
    
    return stock_list

try:
    all_codes = sh_codes + sz_codes + bj_codes
    stock_list = batch_request(all_codes)
    
    # 创建DataFrame
    df = pd.DataFrame(stock_list)
    
    if df.empty:
        print('未获取到任何股票数据')
        exit()
    
    # 剔除ST股票
    df = df[~df['名称'].str.contains('ST', na=False)]
    
    # 剔除科创板股票（688开头）和北交所股票（920开头）
    df = df[~df['代码'].str.startswith(('688', '920'))]
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # PD1分类
    pd1 = [
        '华海药业', '君实生物-U', '汇宇制药-W', '安科生物', '三生国健', '天士力',
        '健康元', '丽珠集团', '诺诚健华', '科伦药业', '恒瑞医药', '复星医药',
        '荣昌生物', '贝达药业', '奥赛康', '微芯生物', '华东医药', '泽璟制药-U'
    ]
    
    # ADC药物分类
    adc_drugs = [
        'ST百灵', '汇宇制药-W', '上海医药', '安科生物', '联化科技', '新华制药',
        '天士力', '诺诚健华', '百奥泰', '科伦药业', '珍宝岛', '荣昌生物', '九洲药业',
        '博济医药', '微芯生物', '泓博医药', '华东医药', '艾德生物', '盟科药业-U',
        '睿智医药', '康龙化成', '新诺威', '迈威生物-U', '百济神州', '昭衍新药', '百利天恒'
    ]
    
    # 创建分类字典
    category_stocks = {
        '全部': df,
        'PD1': df[df['名称'].isin(pd1)],
        'ADC药物': df[df['名称'].isin(adc_drugs)],
    }
    
    # 打印分类统计
    print('\n分类统计:')
    for category, stocks_df in category_stocks.items():
        print(f'  {category}: {len(stocks_df)} 只')
    
    # 打印全部数据
    print('\n创新药概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'创新药_{date_str}.xlsx')
    
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
