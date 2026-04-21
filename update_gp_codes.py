import requests
import json
import re
from datetime import datetime

def get_stocks_from_sina():
    """从新浪财经获取股票数据"""
    all_stocks = []
    
    # 新浪财经API - 获取沪深A股列表
    url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://finance.sina.com.cn/',
    }
    
    page = 1
    max_pages = 100  # 增加页数以获取所有股票
    
    while page <= max_pages:
        params = {
            'page': page,
            'num': 80,
            'sort': 'symbol',
            'asc': 1,
            'node': 'hs_a',
            'symbol': '',
            '_s_r_a': 'page'
        }
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if not data:
                    break
                
                for item in data:
                    code = item.get('symbol', '').strip()
                    name = item.get('name', '')
                    price = item.get('trade', '0')
                    changepercent = item.get('changepercent', '0')
                    
                    # 去掉市场前缀 (sh/sz/bj)
                    if code.startswith(('sh', 'sz', 'bj')):
                        code = code[2:]
                    
                    # 只保留 000/001/002/003/300/301 和 600/601/603/605 开头的股票
                    if code.startswith(('000', '001', '002', '003', '300', '301', '600', '601', '603', '605')):
                        all_stocks.append({
                            '代码': code,
                            '名称': name,
                            '价格': f"{float(price):.3f}" if price else '0.000',
                            '涨跌幅': float(changepercent) if changepercent else 0
                        })
                
                print(f'第 {page} 页，获取 {len(data)} 条，累计 {len(all_stocks)} 只符合条件的股票')
                
                if len(data) < 80:
                    break
                page += 1
            else:
                print(f'请求失败，状态码: {resp.status_code}')
                break
        except Exception as e:
            print(f'获取第 {page} 页失败: {e}')
            break
    
    return all_stocks

def update_gp_codes(stocks):
    """更新 gp_codes.py 文件"""
    # 按代码排序
    stocks.sort(key=lambda x: x['代码'])
    
    # 生成文件内容
    content = f"""# 股票数据文件
# 自动生成，请勿手动修改
# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 股票数量: {len(stocks)}

STOCKS_DATA = [
"""
    
    for stock in stocks:
        content += f"    {{'代码': '{stock['代码']}', '名称': '{stock['名称']}', '价格': '{stock['价格']}', '涨跌幅': {stock['涨跌幅']}}},\n"
    
    content += "]\n"
    
    # 写入文件
    with open('d:/kx724/gp_codes.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'已更新 gp_codes.py，共 {len(stocks)} 只股票')

if __name__ == '__main__':
    print('开始获取股票数据...')
    stocks = get_stocks_from_sina()
    if stocks:
        update_gp_codes(stocks)
        # 统计各类型股票数量
        count_000 = len([s for s in stocks if s['代码'].startswith('000')])
        count_001 = len([s for s in stocks if s['代码'].startswith('001')])
        count_002 = len([s for s in stocks if s['代码'].startswith('002')])
        count_003 = len([s for s in stocks if s['代码'].startswith('003')])
        count_300 = len([s for s in stocks if s['代码'].startswith('300')])
        count_301 = len([s for s in stocks if s['代码'].startswith('301')])
        count_600 = len([s for s in stocks if s['代码'].startswith('600')])
        count_601 = len([s for s in stocks if s['代码'].startswith('601')])
        count_603 = len([s for s in stocks if s['代码'].startswith('603')])
        count_605 = len([s for s in stocks if s['代码'].startswith('605')])
        print(f'\n统计:')
        print(f'000开头: {count_000} 只')
        print(f'001开头: {count_001} 只')
        print(f'002开头: {count_002} 只')
        print(f'003开头: {count_003} 只')
        print(f'300开头: {count_300} 只')
        print(f'301开头: {count_301} 只')
        print(f'600开头: {count_600} 只')
        print(f'601开头: {count_601} 只')
        print(f'603开头: {count_603} 只')
        print(f'605开头: {count_605} 只')
        print(f'总计: {len(stocks)} 只')
    else:
        print('获取股票数据失败')
