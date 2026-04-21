# -*- coding: utf-8 -*-
"""
获取股票逐笔成交数据（Tick数据）
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.eastmoney.com/',
}

def get_tick_data(stock_code):
    """
    获取股票逐笔成交数据（Tick数据）
    
    参数:
        stock_code: 股票代码（如 '300182'）
    """
    # 判断市场代码
    if stock_code.startswith('6'):
        secid = f'1.{stock_code}'  # 沪市
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        secid = f'0.{stock_code}'  # 深市
    else:
        print('不支持的股票代码')
        return None
    
    # 东方财富逐笔成交API
    url = f'http://push2.eastmoney.com/api/qt/stock/details/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&secid={secid}&pos=-0'
    
    print(f'获取 {stock_code} 逐笔成交数据...')
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = json.loads(resp.text)
        
        if data.get('rc') != 0:
            print('获取数据失败')
            return None
        
        details = data.get('data', {}).get('details', [])
        
        if not details:
            print('未获取到数据')
            return None
        
        print(f'获取到 {len(details)} 条逐笔成交数据')
        
        # 解析数据
        # 格式: 时间,价格,成交量,方向,类型
        # 方向：0=卖单，1=买单，2=平盘
        # 类型：4=集合竞价，其他=连续竞价
        tick_data = []
        for item in details:
            parts = item.split(',')
            if len(parts) >= 5:
                time_str = parts[0]
                price = float(parts[1])
                volume = int(parts[2])
                direction = int(parts[3])
                trade_type = int(parts[4])
                
                # 判断买卖方向
                if direction == 1:
                    direction_str = 'B'  # 买单（主动买入）
                elif direction == 0:
                    direction_str = 'S'  # 卖单（主动卖出）
                else:
                    direction_str = '-'  # 平盘
                
                # 判断交易类型
                if trade_type == 4:
                    type_str = '集合竞价'
                else:
                    type_str = '连续竞价'
                
                tick_data.append({
                    '时间': time_str,
                    '价格': price,
                    '成交量(手)': volume,
                    '方向': direction_str,
                    '类型': type_str,
                })
        
        # 创建DataFrame
        df = pd.DataFrame(tick_data)
        
        if not df.empty:
            # 打印数据
            print('\n逐笔成交数据:')
            print('=' * 80)
            print(df.tail(20).to_string(index=False))  # 显示最后20条
            
            # 保存到Excel
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_dir = 'news_data'
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, f'{stock_code}_逐笔成交_{date_str}.xlsx')
            
            df.to_excel(filepath, index=False)
            print(f'\n已保存到: {filepath}')
            print(f'共 {len(df)} 条数据')
        
        return df
        
    except Exception as e:
        print(f'获取数据失败: {e}')
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    stock_code = '300182'
    
    df = get_tick_data(stock_code)
    
    if df is not None:
        print('\n数据统计:')
        print(f'  最高价: {df["价格"].max():.3f}')
        print(f'  最低价: {df["价格"].min():.3f}')
        print(f'  平均成交量: {df["成交量(手)"].mean():.0f}')
        print(f'  总成交量: {df["成交量(手)"].sum():.0f} 手')
        
        # 统计买卖方向
        buy_count = len(df[df['方向'] == 'B'])
        sell_count = len(df[df['方向'] == 'S'])
        print(f'  买单数量: {buy_count}')
        print(f'  卖单数量: {sell_count}')
