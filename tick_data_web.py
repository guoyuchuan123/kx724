# -*- coding: utf-8 -*-
"""
股票逐笔成交数据实时展示Web应用
"""

from flask import Flask, render_template, jsonify, request
import requests
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# 当前股票代码（线程安全）
current_stock_code = ''

# 全局变量存储最新数据
latest_data = {
    'stock_code': '',
    'stock_name': '',
    'pre_price': 0,
    'details': [],
    'last_update': '',
    'alerts': []
}

# 存储上一次的数据用于比较
previous_data = {
    'total_count': 0,
    'last_volumes': []
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.eastmoney.com/',
}

def get_tick_data_api(stock_code):
    """获取逐笔成交数据"""
    if stock_code.startswith('6'):
        secid = f'1.{stock_code}'
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        secid = f'0.{stock_code}'
    else:
        return None
    
    url = f'http://push2.eastmoney.com/api/qt/stock/details/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&secid={secid}&pos=-0'
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = json.loads(resp.text)
        
        if data.get('rc') != 0:
            return None
        
        return data.get('data', {})
    except Exception as e:
        print(f'获取数据失败: {e}')
        return None

def parse_tick_data(details, pre_price):
    """解析逐笔成交数据"""
    tick_data = []
    for item in details:
        parts = item.split(',')
        if len(parts) >= 5:
            time_str = parts[0]
            price = float(parts[1])
            volume = int(parts[2])
            direction = int(parts[3])
            trade_type = int(parts[4])
            
            # 东方财富方向字段：奇数=买入，偶数=卖出
            if direction % 2 == 1:
                direction_str = 'B'
                direction_class = 'buy'
            else:
                direction_str = 'S'
                direction_class = 'sell'
            
            if trade_type == 4:
                type_str = '集合竞价'
            else:
                type_str = '连续竞价'
            
            price_change = price - pre_price if pre_price > 0 else 0
            price_change_pct = (price_change / pre_price * 100) if pre_price > 0 else 0
            
            tick_data.append({
                'time': time_str,
                'price': price,
                'volume': volume,
                'direction': direction_str,
                'direction_class': direction_class,
                'type': type_str,
                'price_change': round(price_change, 2),
                'price_change_pct': round(price_change_pct, 2),
            })
    
    return tick_data

def analyze_volume_alerts(details, pre_price, stock_code, stock_name):
    """分析成交量连续放大情况并生成提示"""
    alerts = []
    
    # 只分析连续竞价阶段的数据
    continuous_details = []
    for item in details:
        parts = item.split(',')
        if len(parts) >= 5:
            trade_type = int(parts[4])
            if trade_type != 4:  # 连续竞价
                continuous_details.append(item)
    
    if len(continuous_details) < 5:
        return alerts
    
    # 获取最新的成交数据（倒序，最新的在前）
    latest_trades = []
    for item in reversed(continuous_details[-20:]):  # 取最后20条
        parts = item.split(',')
        if len(parts) >= 5:
            time_str = parts[0]
            price = float(parts[1])
            volume = int(parts[2])
            direction = int(parts[3])
            
            # 奇数=买入，偶数=卖出
            direction_str = 'B' if direction % 2 == 1 else 'S'
            
            latest_trades.append({
                'time': time_str,
                'price': price,
                'volume': volume,
                'direction': direction_str
            })
    
    if len(latest_trades) < 5:
        return alerts
    
    # 检查最近5笔成交量是否连续放大
    recent_5 = latest_trades[-5:]
    volume_increasing = True
    for i in range(1, len(recent_5)):
        if recent_5[i]['volume'] <= recent_5[i-1]['volume']:
            volume_increasing = False
            break
    
    if volume_increasing:
        # 统计最近5笔的买卖方向
        buy_count = sum(1 for t in recent_5 if t['direction'] == 'B')
        sell_count = sum(1 for t in recent_5 if t['direction'] == 'S')
        current_price = recent_5[-1]['price']
        
        if buy_count >= 3:  # 买入居多
            alerts.append({
                'type': 'buy',
                'message': f'{stock_name}({stock_code}) 当前价{current_price:.2f} 成交量连续放大 买入增多',
                'price': current_price,
                'level': 'warning' if buy_count == 5 else 'info'
            })
        elif sell_count >= 3:  # 卖出居多
            alerts.append({
                'type': 'sell',
                'message': f'{stock_name}({stock_code}) 当前价{current_price:.2f} 成交量连续放大 卖出增多 注意风险',
                'price': current_price,
                'level': 'danger'
            })
    
    # 检查最近5笔成交量都大于2000
    recent_5_volumes = [t['volume'] for t in recent_5]
    if all(v > 2000 for v in recent_5_volumes):
        current_price = recent_5[-1]['price']
        buy_count = sum(1 for t in recent_5 if t['direction'] == 'B')
        
        if buy_count >= 3:
            alerts.append({
                'type': 'buy_signal',
                'message': f'{stock_name}({stock_code}) 当前价{current_price:.2f} 可买入',
                'price': current_price,
                'level': 'success'
            })
    
    # 检查最近5笔成交量都大于3000
    if all(v > 3000 for v in recent_5_volumes):
        current_price = recent_5[-1]['price']
        buy_count = sum(1 for t in recent_5 if t['direction'] == 'B')
        
        if buy_count >= 3:
            alerts.append({
                'type': 'strong_buy',
                'message': f'{stock_name}({stock_code}) 当前价{current_price:.2f} 适度买入',
                'price': current_price,
                'level': 'success'
            })
    
    return alerts


def auto_refresh_data():
    """自动刷新数据"""
    global latest_data, previous_data, current_stock_code
    
    while True:
        try:
            stock_code = current_stock_code
            
            # 如果没有股票代码，跳过刷新
            if not stock_code:
                time.sleep(3)
                continue
            
            data = get_tick_data_api(stock_code)
            
            if data:
                details = data.get('details', [])
                pre_price = float(data.get('prePrice', 0))
                name = data.get('name', '')
                
                parsed_data = parse_tick_data(details, pre_price)
                
                # 分析成交量连续放大情况
                alerts = analyze_volume_alerts(details, pre_price, stock_code, name)
                
                latest_data = {
                    'stock_code': stock_code,
                    'stock_name': name,
                    'pre_price': pre_price,
                    'details': parsed_data,
                    'last_update': datetime.now().strftime('%H:%M:%S'),
                    'total_count': len(parsed_data),
                    'alerts': alerts,
                }
                
                # 更新上一次数据
                previous_data['total_count'] = len(parsed_data)
            
            time.sleep(3)  # 每3秒刷新一次
        except Exception as e:
            print(f'自动刷新失败: {e}')
            time.sleep(5)

@app.route('/')
def index():
    return render_template('tick_data.html')

@app.route('/api/tick_data')
def api_tick_data():
    """API接口：获取逐笔成交数据"""
    global current_stock_code
    
    stock_code = request.args.get('stock_code')
    if stock_code and stock_code != current_stock_code:
        current_stock_code = stock_code
        # 立即刷新数据以确保返回新股票的数据
        data = get_tick_data_api(stock_code)
        if data:
            details = data.get('details', [])
            pre_price = float(data.get('prePrice', 0))
            name = data.get('name', '')
            
            parsed_data = parse_tick_data(details, pre_price)
            
            # 分析成交量连续放大情况
            alerts = analyze_volume_alerts(details, pre_price, stock_code, name)
            
            global latest_data
            latest_data = {
                'stock_code': stock_code,
                'stock_name': name,
                'pre_price': pre_price,
                'details': parsed_data,
                'last_update': datetime.now().strftime('%H:%M:%S'),
                'total_count': len(parsed_data),
                'alerts': alerts,
            }
    
    return jsonify(latest_data)

@app.route('/api/refresh')
def api_refresh():
    """API接口：手动刷新数据"""
    global latest_data, current_stock_code
    
    stock_code = request.args.get('stock_code', current_stock_code)
    
    if stock_code != current_stock_code:
        current_stock_code = stock_code
    
    data = get_tick_data_api(stock_code)
    
    if data:
        details = data.get('details', [])
        pre_price = float(data.get('prePrice', 0))
        name = data.get('name', '')
        
        parsed_data = parse_tick_data(details, pre_price)
        
        # 分析成交量连续放大情况
        alerts = analyze_volume_alerts(details, pre_price, stock_code, name)
        
        latest_data = {
            'stock_code': stock_code,
            'stock_name': name,
            'pre_price': pre_price,
            'details': parsed_data,
            'last_update': datetime.now().strftime('%H:%M:%S'),
            'total_count': len(parsed_data),
            'alerts': alerts,
        }
    
    return jsonify(latest_data)

if __name__ == '__main__':
    # 初始化数据
    stock_code = '300182'
    data = get_tick_data_api(stock_code)
    
    if data:
        details = data.get('details', [])
        pre_price = float(data.get('prePrice', 0))
        name = data.get('name', '')
        
        parsed_data = parse_tick_data(details, pre_price)
        
        latest_data = {
            'stock_code': stock_code,
            'stock_name': name,
            'pre_price': pre_price,
            'details': parsed_data,
            'last_update': datetime.now().strftime('%H:%M:%S'),
            'total_count': len(parsed_data),
        }
    
    # 启动自动刷新线程
    refresh_thread = threading.Thread(target=auto_refresh_data, daemon=True)
    refresh_thread.start()
    
    print('='*60)
    print('股票逐笔成交数据实时展示系统')
    print('='*60)
    print(f'访问地址: http://localhost:5000')
    print('='*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
