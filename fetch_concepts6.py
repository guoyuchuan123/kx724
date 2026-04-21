import requests
import re
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://q.10jqka.com.cn/'}

# 使用同花顺问财API获取概念板块列表
url = 'https://d.10jqka.com.cn/v2/blockrank/885001/8/d10000.js'

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    print(f'Response: {resp.text[:500]}')
    
    # Parse the response
    text = resp.text[:-1]
    text = text.split('{"block":')[-1]
    text = '{"block":' + text
    text = text.replace('null', 'None')
    data = eval(text)
    print(f'Data keys: {data.keys()}')
    print(f'Block: {data.get("block", {})}')
    items = data.get('items', [])
    print(f'Items count: {len(items)}')
    if items:
        print(f'First item: {items[0]}')
except Exception as e:
    print(f'Error: {e}')
