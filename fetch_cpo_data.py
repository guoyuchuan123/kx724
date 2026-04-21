import requests
import json
import pandas as pd
from datetime import datetime
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://q.10jqka.com.cn/',
}

cpo_code = '886033'
blockrank_url = f'https://d.10jqka.com.cn/v2/blockrank/{cpo_code}/10/d10000.js'

print('获取共封装光学(CPO)概念板块数据...')
try:
    resp = requests.get(blockrank_url, headers=headers, timeout=10)
    text = resp.text[:-1]
    text = text.split('{"block":')[-1]
    text = '{"block":' + text
    text = text.replace('null', 'None')
    data = eval(text)
    
    items = data.get('items', [])
    print(f'获取到 {len(items)} 只股票')
    
    # 解析数据
    stock_list = []
    for item in items:
        stock_list.append({
            '代码': item.get('5', ''),
            '名称': item.get('55', ''),
            '价格': float(item.get('10', 0)),
            '成交量': float(item.get('6', 0)),
            '涨跌幅': float(item.get('199112', 0)),
            '涨跌': float(item.get('264648', 0)),
        })
    
    # 创建DataFrame
    df = pd.DataFrame(stock_list)
    
    # 剔除ST股票
    df = df[~df['名称'].str.contains('ST', na=False)]
    
    # 剔除科创板股票（688开头）和北交所股票（920开头）
    df = df[~df['代码'].str.startswith(('688', '920'))]
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # 根据用户提供的准确分类定义
    # 光芯片分类
    optical_chips = [
        '源杰科技', '德明利', '长光华芯', '长芯博创', '仕佳光子', 
        '光迅科技', '华工科技', '可川科技', '永鼎股份', '立昂微', 
        '三安光电', '兆驰股份', '聚飞光电'
    ]
    
    # CPO封装分类
    cpo_packaging = [
        '新易盛', '联特科技', '长芯博创', '剑桥科技', '太辰光', 
        '光迅科技', '华工科技', '沃格光电', '长电科技', '中天科技'
    ]
    
    # MPO连接器分类（用户提供）
    mpo_connectors = [
        '仕佳光子', '光库科技', '天孚通信', '太辰光', 
        '兆龙互连', '杰普特', '致尚科技'
    ]
    
    # 光模块设备分类（用户提供）
    optical_module_equipment = [
        '凯格精机', '快克智能', '科瑞技术', '华盛昌', '联赢激光', 
        '德龙激光', '罗博特科', '奥特维', '深科达', '博众精工', 
        '光力科技', '凌云光', '杰普特', '迈信林', '智立方', 
        '克来机电', '易天股份'
    ]
    
    # 光模块分类（用户提供）
    optical_modules = [
        '长光华芯', '可川科技', '剑桥科技', '沃格光电', '光迅科技', 
        '广合科技', '新易盛', '仕佳光子', '光库科技', '联特科技', 
        '长芯博创', '汇绿生态', '青山纸业', '聚飞光电', '中际旭创', 
        '兆驰股份', '兴森科技', '亨通光电', '腾景科技', '明阳电路', 
        '航天电器', '华工科技', '斯瑞新材', '华丰科技', '中京电子', 
        '生益科技', '强达电路', '九联科技', '博敏电子', '鹏鼎控股', 
        '凌云光', '意华股份', '兆龙互连', '帝奥微', '深科技', 
        '海得控制', '中天科技', '科翔股份', '锐捷网络', '三环集团', 
        '亚康股份', '威尔高', '超声电子', '航锦科技', '弘信电子', 
        '铭普光磁', '立讯精密'
    ]
    
    # 创建分类字典
    category_stocks = {
        '全部': df,
        '光芯片': df[df['名称'].isin(optical_chips)],
        'CPO封装': df[df['名称'].isin(cpo_packaging)],
        'MPO连接器': df[df['名称'].isin(mpo_connectors)],
        '光模块设备': df[df['名称'].isin(optical_module_equipment)],
        '光模块': df[df['名称'].isin(optical_modules)],
    }
    
    # 打印分类统计
    print('\n分类统计:')
    for category, stocks_df in category_stocks.items():
        print(f'  {category}: {len(stocks_df)} 只')
    
    # 打印全部数据
    print('\n共封装光学(CPO)概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'CPO概念_{date_str}.xlsx')
    
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
