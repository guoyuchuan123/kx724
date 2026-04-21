import requests

url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn/',
}

params = {
    'page': 1,
    'num': 10,
    'sort': 'symbol',
    'asc': 1,
    'node': 'hs_a',
}

resp = requests.get(url, params=params, headers=headers, timeout=15)
print(f'状态码: {resp.status_code}')
print(f'响应内容:')
import json
data = resp.json()
for item in data[:5]:
    print(f"  代码: {item.get('symbol')}, 名称: {item.get('name')}, 价格: {item.get('trade')}")
